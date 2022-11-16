import logging
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import import_module, resources
from importlib.resources import Package
from typing import Dict, Iterator, List, Optional, cast

import click
from pydantic import BaseModel, Field

from delfino import commands as delfino_commands
from delfino.constants import COMMANDS_DIRECTORY_NAME
from delfino.models.pyproject_toml import PluginConfig

if sys.version_info < (3, 10):
    from importlib_metadata import distributions
else:
    from importlib.metadata import distributions


_LOG = logging.getLogger(__name__)


def command_names(commands: List[click.Command]) -> str:
    return ", ".join(command.name for command in commands if command.name)


@dataclass(frozen=True)
class _Command:
    name: str
    command: click.Command
    plugin_name: str


class _CommandPackage(BaseModel):
    """Holds `importlib.resources.Package` that include commands and metadata for delfino."""

    plugin_name: str = Field(..., description="Name of the plugin.")
    package: Package = Field(..., description="A package that include commands.")
    # Deprecate, no longer needed once the core package becomes standalone
    required: bool = Field(True, description="One ore more commands from this package is required.")
    # Deprecated once fallback to `tasks` is removed.
    new_name: str = Field(
        "", description="Set when ``package`` is a legacy name and ``new_name`` should be used instead."
    )
    plugin_config: PluginConfig

    class Config:
        arbitrary_types_allowed = True


def find_commands(command_package: _CommandPackage) -> List[_Command]:
    """Finds all instances of ``click.Command`` in given module.

    Does not traverse modules recursively.
    """
    try:
        files = resources.contents(command_package.package)
    except ModuleNotFoundError as exc:
        if command_package.required or f"'{command_package.package}'" not in str(exc):
            raise
        return []

    commands: List[_Command] = []
    package_name: Optional[str] = ""

    for filename in files:
        if filename.startswith("_") or not filename.endswith(".py"):
            continue
        package_name = (
            command_package.package if isinstance(command_package.package, str) else command_package.package.__package__
        )
        command = import_module(f"{package_name}.{filename[:-3]}")

        commands.extend(
            _Command(name=obj.name, command=obj, plugin_name=command_package.plugin_name)
            for obj in vars(command).values()
            if isinstance(obj, click.Command) and obj.name is not None
        )

    if commands and command_package.new_name and package_name:
        click.secho(
            f"⚠ Command module '{package_name}' is deprecated. Please use '{command_package.new_name}' instead.",
            fg="yellow",
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

    LEGACY_LOCAL_COMMAND_FOLDER = "tasks"
    CORE_PLUGIN_NAME = "core"
    TYPE_OF_PLUGIN = "delfino.plugin"

    def __init__(
        self, plugins_configs: Dict[str, PluginConfig], command_packages: Optional[List[_CommandPackage]] = None
    ):
        if command_packages is None:
            self._command_packages = self._default_command_packages(plugins_configs)
        else:
            self._command_packages = command_packages
        self._visible_commands: Dict[str, _Command] = {}
        self._hidden_commands: Dict[str, _Command] = {}
        self._register_packages()

    def __len__(self) -> int:
        return len(self._visible_commands)

    def __getitem__(self, key: str) -> click.Command:
        return self._visible_commands[key].command

    def __iter__(self) -> Iterator[str]:
        return iter(self._visible_commands)

    @property
    def visible_commands(self) -> List[_Command]:
        return list(self._visible_commands.values())

    @property
    def hidden_commands(self) -> List[_Command]:
        return list(self._hidden_commands.values())

    def _default_command_packages(self, plugins_configs: Dict[str, PluginConfig]) -> List[_CommandPackage]:
        # This is a function to lazy load packages in tests. They may not exist on import of the code.
        return [
            # Low priority - core packages distributed with delfino.
            # Will become standalone package in the future.
            _CommandPackage(
                plugin_name=self.CORE_PLUGIN_NAME,
                package=delfino_commands.__package__,
                plugin_config=plugins_configs.get(self.CORE_PLUGIN_NAME, PluginConfig.empty()),
            ),
            # Medium priority - discovered installed packages
            *self._discover_command_packages(plugins_configs),
            # High priority - locally available packages
            _CommandPackage(
                plugin_name=f"local-{COMMANDS_DIRECTORY_NAME}",
                package=COMMANDS_DIRECTORY_NAME,
                required=False,
                plugin_config=plugins_configs.get(f"local-{COMMANDS_DIRECTORY_NAME}", PluginConfig.empty()),
            ),
            # legacy folder name for commands, will be removed in the future
            _CommandPackage(
                plugin_name=f"local-{self.LEGACY_LOCAL_COMMAND_FOLDER}",
                package=self.LEGACY_LOCAL_COMMAND_FOLDER,
                required=False,
                new_name=COMMANDS_DIRECTORY_NAME,
                plugin_config=plugins_configs.get(f"local-{self.LEGACY_LOCAL_COMMAND_FOLDER}", PluginConfig.empty()),
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
            elif plugin_name != cls.CORE_PLUGIN_NAME:
                _LOG.warning(f"Plugin '{plugin_name}' specified in config but no such plugin is installed.")
                command_packages.pop(plugin_name)

        return found_command_packages

    def _register_packages(self):
        for command_package in self._command_packages:
            commands = {command.name: command for command in find_commands(command_package)}
            enabled_commands = command_package.plugin_config.enable_commands or set(commands.keys())
            enabled_commands.difference_update(command_package.plugin_config.disable_commands)

            for command_name, command in commands.items():
                self._register(command, command_name in enabled_commands)

    def _register(self, command: _Command, enabled: bool):
        existing_command = self._visible_commands.pop(command.name, None) or self._hidden_commands.pop(
            command.name, None
        )
        if existing_command:
            _LOG.debug(
                f"Using command '{command.name}' from plugin '{command.plugin_name}'. Previously registered "
                f"by '{existing_command.plugin_name}' plugin, which has lower priority."
            )

        if enabled:
            self._visible_commands[command.name] = command
        else:
            self._hidden_commands[command.name] = command
            _LOG.debug(f"Command '{command.name}' from the '{command.plugin_name}' plugin has been disabled in config.")
