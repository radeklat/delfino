import click

from rads_toolbox.commands.format import run_format
from rads_toolbox.commands.lint import lint
from rads_toolbox.commands.test import test_all
from rads_toolbox.commands.typecheck import typecheck
from rads_toolbox.utils import command_names

_COMMANDS = [run_format, lint, typecheck, test_all]


@click.command(help=f"Runs all checks.\n\nAlias for the {command_names(_COMMANDS)} commands.")
@click.pass_context
def verify_all(click_context: click.Context):
    for command in _COMMANDS:
        click_context.forward(command)
