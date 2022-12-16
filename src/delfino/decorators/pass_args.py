import shlex
from typing import Any

import click

from delfino.click_utils.set_from_config import SetOptionFromConfigCallback


class _SetPassArgsFromConfigCallback(SetOptionFromConfigCallback):
    def _type_cast_value(self, ctx: click.Context, param: click.Parameter, value_from_config: Any) -> Any:
        if isinstance(value_from_config, str):
            value_from_config = tuple(shlex.split(value_from_config))

        return super()._type_cast_value(ctx, param, value_from_config)


_ARGUMENT_NAME = "passed_args"
PASS_ARGS_CALLBACK = _SetPassArgsFromConfigCallback(_ARGUMENT_NAME, "pass_args")


pass_args = click.argument(
    _ARGUMENT_NAME,
    metavar=f"[-- {_ARGUMENT_NAME.upper()}]",
    nargs=-1,
    callback=PASS_ARGS_CALLBACK,
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
