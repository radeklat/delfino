import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Union

import click
import toml
from pydantic import ValidationError

from delfino import commands
from delfino.click_utils.command import find_commands
from delfino.click_utils.completion import install_completion_option, show_completion_option
from delfino.click_utils.help import extended_help_option
from delfino.click_utils.verbosity import log_level_option
from delfino.constants import COMMANDS_DIRECTORY_NAME, ENTRY_POINT, PYPROJECT_TOML_FILENAME
from delfino.contexts import AppContext
from delfino.models.pyproject_toml import PyprojectToml
from delfino.utils import get_package_manager

if sys.version_info < (3, 10):
    from importlib_metadata import Distribution, distributions
else:
    from importlib.metadata import Distribution, distributions


class Commands(click.MultiCommand):

    PRESET_COMMAND_PACKAGE = commands.__package__
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
        self._hidden_commands: Set[str] = set()

        try:
            self._pyproject_toml = PyprojectToml(file_path=pyproject_toml_path, **toml.load(pyproject_toml_path))
            self._hidden_commands = self._pyproject_toml.tool.delfino.disable_commands
            self._hidden_plugin_commands = self._pyproject_toml.tool.delfino.disable_plugin_commands
        except ValidationError as exc:
            self._pyproject_toml = exc
        except FileNotFoundError:
            self._pyproject_toml = PyprojectToml()

        self._commands: Dict[str, click.Command] = {}

    def list_commands(self, ctx: click.Context) -> List[str]:
        """Override to hide commands marked as hidden in the ``pyproject.toml`` file."""
        del ctx
        return sorted(set(self._get_commands().keys()).difference(self._hidden_commands))

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

        if self._hidden_commands:
            if logging.root.level == logging.DEBUG:
                help_str += click.style(
                    f"\n\nDisabled command{'s' if len(self._hidden_commands) > 1 else ''}: "
                    + ", ".join(sorted(self._hidden_commands))
                    + f" (see 'tool.{ENTRY_POINT}.disable_commands' in '{PYPROJECT_TOML_FILENAME}')",
                    fg="white",
                )

        return help_str

    def _get_commands(self) -> Dict[str, click.Command]:
        if self._commands:
            return self._commands

        # default
        self._commands.update(find_commands(self.PRESET_COMMAND_PACKAGE, required=True))

        # external
        self._commands.update(self.ExternalCommandsLoader(self._hidden_plugin_commands).load())

        # local
        self._commands.update(find_commands(COMMANDS_DIRECTORY_NAME, required=False))
        self._commands.update(find_commands("tasks", required=False, new_name=COMMANDS_DIRECTORY_NAME))

        return self._commands

    class ExternalCommandsLoader:

        PLUGIN_GROUP_NAME = "delfino.commands"

        def __init__(self, disabled_commands: Dict[str, Set[str]] = None):
            self.disabled_commands = disabled_commands or {}

        def load(self) -> Dict[str, click.Command]:
            _commands: Dict[str, click.Command] = {}
            for plugin in self._load_plugins():
                for name, command in self._load_commands_for_plugin(plugin):
                    if self._is_disabled_command(plugin.name, name):
                        continue
                    if _commands.get(name, False):
                        raise RuntimeError(
                            f"Command '{name}' is already registered with {plugin.name}-{plugin.version}."
                        )
                    _commands[name] = command
            return _commands

        def _is_disabled_command(self, plugin_name, command_name):
            return command_name in self.disabled_commands.get(plugin_name, set())

        @property
        def _plugin_group_name(self):
            return self.PLUGIN_GROUP_NAME

        def _load_plugins(self) -> Iterator[Distribution]:
            for distribution in distributions():
                for entry_point in distribution.entry_points.select(group=self._plugin_group_name):
                    if not entry_point:
                        continue
                    yield distribution

        @staticmethod
        def _load_commands_for_plugin(plugin: Distribution) -> Iterator[Tuple[str, click.Command]]:
            for entry_point in plugin.entry_points:
                package = entry_point.load()
                for name, command in find_commands(package, required=True).items():
                    yield name, command


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
