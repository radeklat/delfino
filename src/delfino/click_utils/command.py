import logging
import sys
from dataclasses import dataclass
from functools import partial
from importlib import import_module, resources
from importlib.resources import Package
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Set, cast

import click
from pydantic import BaseModel, ConfigDict, Field, field_validator

from delfino.constants import DEFAULT_LOCAL_COMMAND_FOLDERS, PYPROJECT_TOML_FILENAME
from delfino.models.pyproject_toml import PluginConfig

if sys.version_info < (3, 10):
    # `importlib.metadata` available since 3.8 but `distribution.entry_points.select` only since 3.10
    from importlib_metadata import distributions
else:
    from importlib.metadata import distributions


_LOG = logging.getLogger(__name__)


def command_names(commands: List[click.Command]) -> str:
    return ", ".join(command.name for command in commands if command.name)


class _CommandPackage(BaseModel):
    """Holds `importlib.resources.Package` that include commands and metadata for delfino."""

    plugin_name: str = Field(..., description="Name of the plugin.")
    package: Package = Field(..., description="A package that include commands.")
    plugin_config: PluginConfig

    @field_validator("package")
    @classmethod
    def package_is_valid(cls, value: Package):  # pylint: disable=no-self-argument
        if isinstance(value, str):
            return value
        if isinstance(value.__package__, str) and isinstance(value.__file__, str):
            return value

        raise ValueError(
            f"`package` must be either an instance of `str` or have the `__module__` and "
            f"`__file__` attributes set to a `str` but '{value}' used."
        )

    @property
    def module_name(self) -> str:
        if isinstance(self.package, str):
            return self.package
        assert isinstance(self.package.__package__, str)
        return self.package.__package__

    @property
    def module_root_dir(self) -> Path:
        if isinstance(self.package, str):
            return Path(self.package)
        assert isinstance(self.package.__file__, str)
        return Path(self.package.__file__).parent

    model_config = ConfigDict(arbitrary_types_allowed=True)


@dataclass(frozen=True)
class _Command:
    name: str
    command: click.Command
    package: _CommandPackage


def find_commands(command_package: _CommandPackage) -> List[_Command]:
    """Finds all instances of ``click.Command`` in given module.

    Does not traverse modules recursively. Plugins must point to the correct module via the entry point.
    """
    try:
        if sys.version_info >= (3, 9):
            files = [
                path.name for path in resources.files(command_package.package).iterdir()  # pylint: disable=no-member
            ]
        else:
            files = resources.contents(command_package.package)
    except ModuleNotFoundError:
        return []

    commands: List[_Command] = []

    for filename in files:
        if not filename.endswith(".py") or (filename.startswith("_") and filename != "__init__.py"):
            continue
        module = import_module(f"{command_package.module_name}.{filename[:-3]}")

        commands.extend(
            _Command(name=obj.name, command=obj, package=command_package)
            for obj_name, obj in vars(module).items()
            if not obj_name.startswith("_") and isinstance(obj, click.Command) and obj.name is not None
        )

    return commands


def get_root_command(click_context: click.Context) -> click.MultiCommand:
    """Find the root command.

    In the context of `delfino`, this is generally the ``main.Commands`` instance.
    """
    while click_context.parent:
        click_context = click_context.parent
    return cast(click.MultiCommand, click_context.command)


class CommandRegistry(Mapping):
    """An internal command registry which can raise error with duplicated commands.

    The purpose of this class is to keep track on registered commands and raise an
    error if a command with the same name is registered twice.

    The error will be raised only when a command is from plugins. Local commands can
    always override existing commands.
    """

    TYPE_OF_PLUGIN = "delfino.plugin"
    LOCAL_PLUGIN_NAME = "local"

    def __init__(
        self,
        plugins_configs: Dict[str, PluginConfig],
        command_packages: Optional[List[_CommandPackage]] = None,
        local_command_folders: Iterable[Path] = DEFAULT_LOCAL_COMMAND_FOLDERS,
    ):
        if command_packages is None:
            self._command_packages = self._default_command_packages(plugins_configs, local_command_folders)
        else:
            self._command_packages = command_packages
        self._visible_commands: Dict[str, _Command] = {}
        self._hidden_commands: Dict[str, _Command] = {}
        self._register_packages()

    def __len__(self) -> int:
        return len(self._visible_commands)

    def __getitem__(self, key: str) -> _Command:
        return self._visible_commands[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._visible_commands)

    @property
    def visible_commands(self) -> List[_Command]:
        return list(self._visible_commands.values())

    @property
    def hidden_commands(self) -> List[_Command]:
        return list(self._hidden_commands.values())

    @classmethod
    def _default_command_packages(
        cls, plugins_configs: Dict[str, PluginConfig], local_command_folders: Iterable[Path]
    ) -> List[_CommandPackage]:
        # This is a function to lazy load packages in tests. They may not exist on import of the code.
        return [
            # Lower priority - discovered installed packages
            *cls._discover_command_packages(plugins_configs),
            # Higher priority - locally available packages
            *(
                _CommandPackage(
                    plugin_name=cls.LOCAL_PLUGIN_NAME,
                    package=str(local_commands_folder),
                    plugin_config=plugins_configs.get(cls.LOCAL_PLUGIN_NAME, PluginConfig.empty()),
                )
                for local_commands_folder in local_command_folders
            ),
        ]

    @classmethod
    def _discover_command_packages(cls, plugins_configs: Dict[str, PluginConfig]) -> List[_CommandPackage]:
        """Discover packages from plugin. It is using package metadata as plugin discovering solution.

        Check the following URL about the plugin discovering solutions including the one uses package metadata.
        https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
        """
        # We want to keep loaded _CommandPackage instance in the same order as defined in the config
        command_packages: Dict[str, Optional[_CommandPackage]] = {plugin_name: None for plugin_name in plugins_configs}
        for distribution in distributions():
            for entry_point in distribution.entry_points.select(group=cls.TYPE_OF_PLUGIN):
                if not entry_point:
                    continue
                plugin_name = distribution.metadata["Name"]
                if plugin_name not in command_packages:
                    continue
                command_packages[plugin_name] = _CommandPackage(
                    plugin_name=plugin_name,
                    package=entry_point.load(),
                    plugin_config=plugins_configs.get(plugin_name, PluginConfig.empty()),
                )

        found_command_packages = []
        for plugin_name, command_package in list(command_packages.items()):
            if command_package is not None:
                found_command_packages.append(command_package)
            else:
                if plugin_name != cls.LOCAL_PLUGIN_NAME:
                    _LOG.warning(f"Plugin '{plugin_name}' specified in config but no such plugin is installed.")
                command_packages.pop(plugin_name)

        return found_command_packages

    @staticmethod
    def _filter_and_log_invalid_command_names(
        plugin_name: str, available_command_names: Set[str], group_name: str, group_command_names: Set[str]
    ) -> Set[str]:
        missing_commands = group_command_names - available_command_names
        for command_name in missing_commands:
            _LOG.warning(
                f"{group_name} command '{command_name}' from the '{plugin_name}' plugin "
                "in config does not exist. This can be a typo in the command name or "
                f"the command has been removed/renamed. Please update the '{PYPROJECT_TOML_FILENAME}' file."
            )
        return group_command_names - missing_commands if missing_commands else group_command_names

    def _register_packages(self):
        for command_package in self._command_packages:
            commands = {command.name: command for command in find_commands(command_package)}
            available_command_names = set(commands.keys())

            filter_and_log_invalid_command_names = partial(
                self._filter_and_log_invalid_command_names, command_package.plugin_name, available_command_names
            )

            disabled_commands = filter_and_log_invalid_command_names(
                "Disabled", command_package.plugin_config.disable_commands
            )

            enabled_commands = filter_and_log_invalid_command_names(
                "Enabled", command_package.plugin_config.enable_commands or available_command_names
            )

            enabled_commands.difference_update(disabled_commands)

            for command_name, command in commands.items():
                self._register(command, command_name in enabled_commands)

    def _register(self, command: _Command, enabled: bool):
        existing_command = self._visible_commands.pop(command.name, None) or self._hidden_commands.pop(
            command.name, None
        )
        if existing_command:
            _LOG.debug(
                f"Using command '{command.name}' from plugin '{command.package.plugin_name}'. Previously registered "
                f"by '{existing_command.package.plugin_name}' plugin, which has lower priority."
            )

        if enabled:
            self._visible_commands[command.name] = command
        else:
            self._hidden_commands[command.name] = command
            _LOG.debug(
                f"Command '{command.name}' from the '{command.package.plugin_name}' plugin has been disabled in config."
            )
