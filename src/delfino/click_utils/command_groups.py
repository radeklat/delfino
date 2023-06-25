from collections import ChainMap
from logging import getLogger
from typing import Dict, List, cast

import click

from delfino.click_utils.command import get_root_command
from delfino.decorators.files_folders import FILES_FOLDERS_OPTION_CALLBACK
from delfino.decorators.pass_args import PASS_ARGS_CALLBACK
from delfino.models.app_context import AppContext

_LOG = getLogger(__name__)


def get_command_groups(app_context: AppContext) -> Dict[str, List[str]]:
    return {**app_context.plugin_config.command_groups, **app_context.pyproject_toml.tool.delfino.command_groups}


def _get_target_command_names(group_name: str, app_context: AppContext) -> List[str]:
    if (target_command_names := get_command_groups(app_context).get(group_name, None)) is None:
        raise click.exceptions.Abort(f"Command group '{group_name}' does not exist.")

    if not target_command_names:
        _LOG.warning(f"Command group '{group_name}' contains no commands.")
        raise click.exceptions.Exit()

    return target_command_names


def execute_commands_group(group_name: str, click_context: click.Context, app_context: AppContext, **kwargs):
    target_command_names = _get_target_command_names(group_name, app_context)
    root_command = get_root_command(click_context)

    commands: Dict[str, click.Command] = {
        command: cast(click.Command, root_command.get_command(click_context, command))
        for command in root_command.list_commands(click_context)
    }

    for target_name in target_command_names:
        if target_name not in commands:
            _LOG.warning(f"Command '{target_name}' from the '{group_name}' command group does not exist. Skipping.")
            continue

        if target_name in app_context.plugin_config.disable_commands:
            _LOG.debug(f"Skipping disabled command '{target_name}'.")
            continue

        command = commands[target_name]

        parameter_from_config = ChainMap(
            *(
                callback.parameter_from_config_in_group(click_context, command)
                for callback in [PASS_ARGS_CALLBACK, FILES_FOLDERS_OPTION_CALLBACK]
            )
        )

        click_context.forward(command, **kwargs, **parameter_from_config)
