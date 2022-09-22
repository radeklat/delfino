import logging
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import click
import toml
from pydantic import ValidationError

from delfino import commands as delfino_commands
from delfino.click_utils.command import find_commands
from delfino.click_utils.completion import install_completion_option, show_completion_option
from delfino.click_utils.help import extended_help_option
from delfino.click_utils.verbosity import log_level_option
from delfino.constants import COMMANDS_DIRECTORY_NAME, ENTRY_POINT, PYPROJECT_TOML_FILENAME
from delfino.contexts import AppContext
from delfino.models.command_package import CommandPackage
from delfino.models.pyproject_toml import PyprojectToml
from delfino.plugin import discover_packages
from delfino.utils import get_package_manager


class Commands(click.MultiCommand):

    PRESET_COMMAND_PACKAGE = delfino_commands.__package__
    DEFAULT_COMMAND_PACKAGE = COMMANDS_DIRECTORY_NAME
    DEPRECATED_COMMAND_PACKAGES = ["tasks"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sys.path.append(os.getcwd())

        self._project_root = Path(os.getcwd())
        pyproject_toml_path = (self._project_root / PYPROJECT_TOML_FILENAME).relative_to(self._project_root)

        # When evaluating available commands, the program should not fail. We save the exception
        # to show it only when a command is executed.
        self._pyproject_toml: Union[PyprojectToml, Exception]
        self._hidden_plugin_commands: Dict[str, Set[str]] = {}

        try:
            self._pyproject_toml = PyprojectToml(file_path=pyproject_toml_path, **toml.load(pyproject_toml_path))
            self._hidden_plugin_commands = self._pyproject_toml.tool.delfino.disable_plugin_commands
            # Temporal code to deprecate tool.delfino.disable_commands
            if self._pyproject_toml.tool.delfino.disable_commands:
                self._hidden_plugin_commands["delfino"] = self._pyproject_toml.tool.delfino.disable_commands
        except ValidationError as exc:
            self._pyproject_toml = exc
        except FileNotFoundError:
            self._pyproject_toml = PyprojectToml()

        self._commands: Dict[str, click.Command] = {}

    def list_commands(self, ctx: click.Context) -> List[str]:
        """Override as MultiCommand always returns []."""
        del ctx
        return sorted(set(self._get_commands().keys()))

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        """Override to give all commands a common ``AppContext`` or fail if ``pyproject.toml`` is broken/missing."""
        cmd = self._get_commands().get(cmd_name, None)

        if ctx.resilient_parsing:  # do not fail on auto-completion
            return cmd

        if isinstance(self._pyproject_toml, Exception):
            click.secho(f"Delfino appears to be misconfigured: {self._pyproject_toml}", fg="red", err=True)
            raise click.Abort() from self._pyproject_toml

        ctx.obj = AppContext(
            project_root=self._project_root,
            pyproject_toml=self._pyproject_toml,
            package_manager=get_package_manager(self._project_root, self._pyproject_toml),
        )

        return cmd

    def invoke(self, ctx: click.Context) -> Any:
        """Override to turn ``AssertionError`` exception into ``click.exceptions.Exit``."""
        try:
            return super().invoke(ctx)
        except AssertionError as exc:
            click.secho(f"Command '{ctx.invoked_subcommand}' is misconfigured. {exc}", fg="red", err=True)
            raise click.exceptions.Exit(1)

    def get_help(self, *args, **kwargs) -> str:
        help_str = super().get_help(*args, **kwargs)

        if self._hidden_plugin_commands:
            if logging.root.level == logging.DEBUG:
                help_str += click.style(
                    f"\n\nDisabled command{'s' if len(self._hidden_plugin_commands) > 1 else ''}: "
                    + ", ".join(sorted([f"{plugin}.{cmd}" for plugin, cmd in self._hidden_plugin_commands.items()]))
                    + f" (see 'tool.{ENTRY_POINT}.disable_plugin_commands' in '{PYPROJECT_TOML_FILENAME}')",
                    fg="white",
                )

        return help_str

    def _get_commands(self) -> Dict[str, click.Command]:
        if self._commands:
            return self._commands

        command_packages = [
            CommandPackage(package=self.PRESET_COMMAND_PACKAGE, plugin_name="delfino"),
            *list(discover_packages()),
            CommandPackage(package=COMMANDS_DIRECTORY_NAME, required=False),
            CommandPackage(package="tasks", required=False, new_name=COMMANDS_DIRECTORY_NAME),
        ]

        registry = _CommandRegistry(self._hidden_plugin_commands)
        for command_package in command_packages:
            registry.register_command_package(command_package)

        self._commands = registry.as_dict()

        return self._commands


class _CommandRegistry:
    """An internal command registry which can raise error with duplicated commands.

    The purpose of this class is to keep track on registered commands and raise an
    error if a command with the same name is registered twice.

    The error will be raised only when a command is from plugins. Local commands can
    always override existing commands.
    """

    @dataclass
    class Command:
        command: click.Command
        plugin_name: str

    def __init__(self, disabled_command: Dict[str, Set[str]]):
        self._disabled_command = defaultdict(set, disabled_command)
        self._commands: Dict[str, _CommandRegistry.Command] = {}

    def register_command_package(self, command_package: CommandPackage):
        for name, command in find_commands(
            command_package.package, required=command_package.required, new_name=command_package.new_name
        ).items():
            self.register(name, command, plugin_name=command_package.plugin_name)

    def register(self, name: str, command: click.Command, plugin_name=""):
        if name in self._disabled_command[plugin_name]:
            return
        # When a command is from a plugin check if a command with the same name is already registered
        # Otherwise (= local commands) overwrite existing command
        if plugin_name:
            existing_command = self._commands.get(name)
            if existing_command:
                raise RuntimeError(f"Command '{name}' is already registered with {existing_command.plugin_name}.")
        self._commands[name] = self.Command(command, plugin_name)

    def as_dict(self):
        return {name: cmd.command for name, cmd in self._commands.items()}


@click.group(cls=Commands)
@extended_help_option
@click.version_option()
@log_level_option
@show_completion_option
@install_completion_option
def main(log_level=None):
    del log_level


if __name__ == "__main__":
    main()
