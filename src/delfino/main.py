import logging
import os
import sys
from pathlib import Path
from typing import Any, List, Optional

import click

from delfino.click_utils.command import CommandRegistry
from delfino.config import ConfigValidationError, load_config
from delfino.constants import ENTRY_POINT, PYPROJECT_TOML_FILENAME
from delfino.internal_parameters.completion import install_completion_option, show_completion_option
from delfino.internal_parameters.help import extended_help_option
from delfino.internal_parameters.verbosity import log_level_option
from delfino.models.app_context import AppContext
from delfino.models.pyproject_toml import PyprojectToml
from delfino.utils import get_package_manager


class Commands(click.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sys.path.append(os.getcwd())

        self._project_root = Path(os.getcwd())

        # When evaluating available commands, the program should not fail. We save the exception
        # to show it only when a command is executed.
        self._pyproject_toml_validation_error: Optional[ConfigValidationError] = None

        try:
            self._pyproject_toml = load_config(self._project_root)
        except ConfigValidationError as exc:
            self._pyproject_toml = PyprojectToml()
            self._pyproject_toml_validation_error = exc

        self._command_registry = CommandRegistry(
            plugins_configs=self._pyproject_toml.tool.delfino.plugins,
            local_command_folders=self._pyproject_toml.tool.delfino.local_command_folders,
        )

    def list_commands(self, ctx: click.Context) -> List[str]:
        """Override as MultiCommand always returns []."""
        del ctx
        return sorted(command.name for command in self._command_registry.visible_commands)

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        """Override to give all commands a common ``AppContext`` or fail if ``pyproject.toml`` is broken/missing."""
        if (cmd := self._command_registry.get(cmd_name, None)) is None:
            return None  # command doesn't exist

        if ctx.resilient_parsing:  # do not fail on auto-completion
            return cmd.command

        if self._pyproject_toml_validation_error:
            click.secho(str(self._pyproject_toml_validation_error), fg="red", err=True)
            raise click.Abort() from self._pyproject_toml_validation_error

        ctx.obj = AppContext(
            project_root=self._project_root,
            pyproject_toml=self._pyproject_toml,
            package_manager=get_package_manager(self._project_root, self._pyproject_toml),
            plugin_config=cmd.package.plugin_config,
        )

        return cmd.command

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
                                f"{command.package.plugin_name}/{command.command.name}"
                                for command in self._command_registry.hidden_commands
                            ]
                        )
                    )
                    + f" (see 'tool.{ENTRY_POINT}.<PLUGIN NAME>.disable_commands' in '{PYPROJECT_TOML_FILENAME}')",
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
