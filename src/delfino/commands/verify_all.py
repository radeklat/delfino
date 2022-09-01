from typing import Dict, cast

import click

from delfino.click_utils.command import get_root_command
from delfino.commands.format import run_format
from delfino.commands.lint import lint
from delfino.commands.test import test_all
from delfino.commands.typecheck import typecheck
from delfino.contexts import AppContext, pass_app_context

_COMMANDS = [run_format, lint, typecheck, test_all]


@click.command(help="Runs all verification commands. Configured by the ``verify_commands`` setting.")
@click.pass_context
@pass_app_context
def verify_all(app_context: AppContext, click_context: click.Context):
    delfino = app_context.pyproject_toml.tool.delfino

    root = get_root_command(click_context)
    commands: Dict[str, click.Command] = {
        command: cast(click.Command, root.get_command(click_context, command))
        for command in root.list_commands(click_context)
    }

    target_commands = [
        commands[target_name]
        for target_name in delfino.verify_commands
        if target_name in commands and target_name not in delfino.disable_commands
    ]

    for command in target_commands:
        click_context.forward(command)
