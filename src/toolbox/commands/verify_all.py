import click

from toolbox.commands.format import run_format
from toolbox.commands.lint import lint
from toolbox.commands.test import test_all
from toolbox.commands.typecheck import typecheck

_COMMANDS = [run_format, lint, typecheck, test_all]


@click.command(help=f"Runs all checks.\n\nAlias for the {', '.join(command.name for command in _COMMANDS)} commands.")
@click.pass_context
def verify_all(click_context: click.Context):
    for command in _COMMANDS:
        click_context.forward(command)
