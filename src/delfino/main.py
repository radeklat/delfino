import logging
import os
import sys
from pathlib import Path
from typing import Any, List, Optional, Union
from warnings import warn

import click
import toml
from pydantic import ValidationError

from delfino.click_utils.command import CommandRegistry
from delfino.click_utils.completion import install_completion_option, show_completion_option
from delfino.click_utils.help import extended_help_option
from delfino.click_utils.verbosity import log_level_option
from delfino.constants import ENTRY_POINT, PYPROJECT_TOML_FILENAME
from delfino.contexts import AppContext
from delfino.models.pyproject_toml import PluginConfig, PyprojectToml
from delfino.utils import get_package_manager


class Commands(click.MultiCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sys.path.append(os.getcwd())

        self._project_root = Path(os.getcwd())
        pyproject_toml_path = (self._project_root / PYPROJECT_TOML_FILENAME).relative_to(self._project_root)

        # When evaluating available commands, the program should not fail. We save the exception
        # to show it only when a command is executed.
        self._pyproject_toml: Union[PyprojectToml, Exception]

        try:
            self._pyproject_toml = PyprojectToml(file_path=pyproject_toml_path, **toml.load(pyproject_toml_path))

            plugins = self._pyproject_toml.tool.delfino.plugins

            # Temporary code to deprecate tool.delfino.disable_commands
            if self._pyproject_toml.tool.delfino.disable_commands:
                plugins[CommandRegistry.CORE_PLUGIN_NAME] = PluginConfig(
                    disable_commands=self._pyproject_toml.tool.delfino.disable_commands
                )
                warn(
                    f"```\n[tool.delfino]\ndisable_commands = ...\n```\nconfiguration option "
                    f"in `pyproject.toml` is deprecated and will be removed in the future. Please use\n"
                    f"```\n[tool.delfino.plugins.{CommandRegistry.CORE_PLUGIN_NAME}]\ndisable_commands = ...\n```\n"
                    f"instead.",
                    DeprecationWarning,
                )
        except ValidationError as exc:
            self._pyproject_toml = exc
        except FileNotFoundError:
            self._pyproject_toml = PyprojectToml()

        self._command_registry = CommandRegistry(plugins)

    def list_commands(self, ctx: click.Context) -> List[str]:
        """Override as MultiCommand always returns []."""
        del ctx
        return sorted(command.name for command in self._command_registry.visible_commands)

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        """Override to give all commands a common ``AppContext`` or fail if ``pyproject.toml`` is broken/missing."""
        cmd = self._command_registry.get(cmd_name, None)

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

        if self._command_registry.hidden_commands:
            if logging.root.level == logging.DEBUG:
                help_str += click.style(
                    f"\n\nDisabled command{'s' if len(self._command_registry.hidden_commands) > 1 else ''}: "
                    + ", ".join(
                        sorted(
                            [
                                f"{command.plugin_name}/{command.command.name}"
                                for command in self._command_registry.hidden_commands
                            ]
                        )
                    )
                    + f" (see 'tool.{ENTRY_POINT}.disable_plugin_commands' in '{PYPROJECT_TOML_FILENAME}')",
                    fg="white",
                )

        return help_str


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
