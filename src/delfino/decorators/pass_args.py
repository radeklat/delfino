import shlex
from logging import getLogger
from typing import Tuple

import click

from delfino.models.app_context import AppContext

_CONFIG_NAME = "pass_args"
_ARGUMENT_NAME = "passed_args"
_LOG = getLogger(__name__)


def _set_passed_args_from_config(ctx: click.Context, param, value) -> Tuple[str, ...]:
    """Load passed arguments from config if none given on command line."""
    del param

    # Command line options have higher priority. Return them instead of options from the config file.
    if value:
        return value

    # No command line options provided, try to load them from config
    app_context = ctx.find_object(AppContext)

    if app_context is None:
        raise RuntimeError("AppContext was expected to be set but none found.")

    command_name: str = ctx.command.name or ""
    passed_args: str = getattr(app_context.plugin_config, command_name, {}).get(_CONFIG_NAME, None)
    if passed_args:
        return tuple(shlex.split(passed_args))

    return value


def set_passed_args_from_config_in_group(ctx: click.Context, command: click.Command):
    """Same as ``_set_passed_args_from_config`` but called on a given command.

    This is useful for invoking commands indirectly, for example in a group command.
    """
    app_context = ctx.find_object(AppContext)

    if app_context is None:
        raise RuntimeError("AppContext was expected to be set but none found.")

    command_config = getattr(app_context.plugin_config, command.name or "", {})

    if isinstance(command_config, dict):
        passed_args = command_config.get(_CONFIG_NAME, None)
    else:
        passed_args = getattr(command_config, _CONFIG_NAME, None)

    if passed_args:
        for command_param in command.params:
            if isinstance(command_param, click.Argument) and command_param.name == _ARGUMENT_NAME:
                ctx.params[_ARGUMENT_NAME] = tuple(shlex.split(passed_args))
                return
        _LOG.warning(
            f"Command '{command.name}' has no parameter '{_ARGUMENT_NAME}'. Please update the "
            f"pyproject.toml file, option '{command.name}.{_CONFIG_NAME}'."
        )


pass_args = click.argument(
    _ARGUMENT_NAME,
    metavar=f"[-- {_ARGUMENT_NAME.upper()}]",
    nargs=-1,
    callback=_set_passed_args_from_config,
    type=click.UNPROCESSED,
)
"""A command decorator which passes additional arguments to the decorated command.

Example:

    @click.command("test")
    @pass_args
    def run_pytest(passed_args: List[str]):
        run(["pytest", *passed_args])

This decorator adds a ``passed_args`` parameter containing all the additional passed arguments
from one of the following sources:
    - The ``pyproject.toml`` file, under ``tools.delfino.<PLUGIN>.<COMMAND>.pass_args``. Example:

        [tool.delfino.plugins.delfino-core.test]
        pass_args = '--capture=no'

    - From commands line, capturing anything after ``--``. Example:

        delfino test -- --capture=no

Note:
    This decorator will not automatically pass the argument to the wrapped
    command. You need to do it manually.
"""
