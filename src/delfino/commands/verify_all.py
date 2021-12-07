import click

from delfino.click_utils.command import command_names
from delfino.commands.format import run_format
from delfino.commands.lint import lint
from delfino.commands.test import test_all
from delfino.commands.typecheck import typecheck

_COMMANDS = [run_format, lint, typecheck, test_all]


@click.command(help=f"Runs all checks.\n\nAlias for the {command_names(_COMMANDS)} commands.")
@click.pass_context
def verify_all(click_context: click.Context):
    for command in _COMMANDS:
        click_context.forward(command)
