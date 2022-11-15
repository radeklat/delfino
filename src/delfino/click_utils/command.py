import logging
import sys
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import import_module, resources
from importlib.resources import Package
from typing import Dict, Iterator, List, Optional, Set, cast

import click
from pydantic import BaseModel, Field

from delfino import commands as delfino_commands
from delfino.constants import COMMANDS_DIRECTORY_NAME

if sys.version_info < (3, 10):
    from importlib_metadata import distributions
else:
    from importlib.metadata import distributions


_LOG = logging.getLogger(__name__)


def command_names(commands: List[click.Command]) -> str:
    return ", ".join(command.name for command in commands if command.name)


@dataclass
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

        for obj in vars(command).values():
            if isinstance(obj, click.Command) and obj.name is not None:
                commands.append(_Command(name=obj.name, command=obj, plugin_name=command_package.plugin_name))

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

    def __init__(
        self, disabled_commands: Dict[str, Set[str]], command_packages: Optional[List[_CommandPackage]] = None
    ):
        self._command_packages = command_packages or [
            # Low priority - core packages distributed with delfino.
            # Will become standalone package in the future.
            _CommandPackage(plugin_name=self.CORE_PLUGIN_NAME, package=delfino_commands.__package__),
            # Medium priority - discovered installed packages
            *list(self._discover_command_packages()),
            # High priority - locally available packages
            _CommandPackage(
                plugin_name=f"local ({COMMANDS_DIRECTORY_NAME})", package=COMMANDS_DIRECTORY_NAME, required=False
            ),
            # legacy folder name for commands, will be removed in the future
            _CommandPackage(
                plugin_name=f"local ({self.LEGACY_LOCAL_COMMAND_FOLDER})",
                package=self.LEGACY_LOCAL_COMMAND_FOLDER,
                required=False,
                new_name=COMMANDS_DIRECTORY_NAME,
            ),
        ]
        self._commands: Dict[str, _Command] = {}
        self._hidden_commands: Set[_Command] = set()
        self._register_packages(defaultdict(set, disabled_commands))

    def __len__(self) -> int:
        return len(self._commands)

    def __getitem__(self, key: str) -> click.Command:
        return self._commands[key].command

    def __iter__(self) -> Iterator[str]:
        return iter(self._commands)

    @property
    def visible_commands(self) -> List[str]:
        return sorted(self._commands.keys())

    @property
    def hidden_commands(self) -> List[_Command]:
        return list(self._hidden_commands)

    @staticmethod
    def _discover_command_packages(plugin_group_name: str = "delfino.commands") -> Iterator[_CommandPackage]:
        """Discover packages from plugin. It is using package metadata as plugin discovering solution.

        Check the following URL about the plugin discovering solutions including the one uses package metadata.
        https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/

        Args:
            plugin_group_name (str): Used for a key to filter plugin for Delfino. Defaults to "delfino.commands".

        Yields:
            Iterator[_CommandPackage]: Iterator of models._CommandPackage.
        """
        for distribution in distributions():
            for entry_point in distribution.entry_points.select(group=plugin_group_name):
                if not entry_point:
                    continue
                yield _CommandPackage(plugin_name=distribution.metadata["Name"], package=entry_point.load())

    def _register_packages(self, disabled_commands):
        for command_package in self._command_packages:
            for command in find_commands(command_package):
                if command.name in disabled_commands:
                    self._hidden_commands.add(command)
                else:
                    self._register(command)

    def _register(self, command: _Command):
        existing_command = self._commands.get(command.name)
        if existing_command:
            _LOG.debug(
                f"Using command '{command.name}' from plugin '{command.plugin_name}'. Previously registered "
                f"by '{existing_command.plugin_name}' plugin, which has lower priority."
            )
        self._commands[command.name] = command
