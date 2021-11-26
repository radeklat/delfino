import os
import sys
from pathlib import Path
from typing import Optional

import click
import toml
from pydantic import ValidationError

from delfino import commands
from delfino.commands.init import run_init
from delfino.constants import ENTRY_POINT, PYPROJECT_TOML
from delfino.contexts import AppContext
from delfino.models.pyproject_toml import PyprojectToml
from delfino.utils import find_commands, get_package_manager


@click.group()
@click.option(
    "--project-root",
    default=None,
    type=click.Path(exists=True, dir_okay=True, file_okay=False, readable=True, writable=True),
    help="Root folder of the project, if not running from it.",
)
def main(project_root: Optional[Path] = None):
    if not project_root:
        project_root = Path(os.getcwd())

    file_path = (project_root / PYPROJECT_TOML).relative_to(project_root)
    context = click.get_current_context()

    if context.invoked_subcommand == run_init.name:
        context.obj = file_path
        return

    try:
        py_project_toml = PyprojectToml(file_path=file_path, **toml.load(file_path))
    except (FileNotFoundError, ValidationError) as exc:
        click.secho(
            f"Delfino appears to be misconfigured: {exc}\nPlease run `{ENTRY_POINT} {run_init.name}`.",
            fg="red",
            err=True,
        )
        raise click.Abort() from exc

    context.obj = AppContext(
        project_root=project_root,
        py_project_toml=py_project_toml,
        package_manager=get_package_manager(project_root, py_project_toml),
    )


sys.path.append(os.getcwd())

_COMMANDS = find_commands(commands.__package__, required=True)
_COMMANDS.extend(find_commands("commands", required=False))
_COMMANDS.extend(find_commands("tasks", required=False, new_name="commands"))

for command in _COMMANDS:
    main.add_command(command, command.name)

if __name__ == "__main__":
    main()
