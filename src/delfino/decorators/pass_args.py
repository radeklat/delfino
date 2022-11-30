import shlex
from typing import Tuple

import click

from delfino.models.app_context import AppContext

_ARGUMENT_NAME = "passed_args"


def _set_passed_args_from_config(ctx, param, value) -> Tuple[str, ...]:
    del param

    # Command line options have higher priority. Return them instead of options from the config file.
    if value:
        return value

    # No command line options provided, try to load them from config
    app_context: AppContext = ctx.find_object(AppContext)
    command_name: str = ctx.command.name
    passed_args: str = getattr(app_context.plugin_config, command_name, {}).get("pass_args", None)
    if passed_args:
        return tuple(shlex.split(passed_args))

    return value


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
