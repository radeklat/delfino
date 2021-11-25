import os
from pathlib import Path
from typing import Optional

import click
import toml
from pydantic import ValidationError

from rads_toolbox import commands
from rads_toolbox.commands.init import run_init
from rads_toolbox.constants import PYPROJECT_TOML
from rads_toolbox.contexts import AppContext
from rads_toolbox.models.pyproject_toml import PyprojectToml
from rads_toolbox.utils import find_commands, get_package_manager


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
            f"Toolbox appears to be misconfigured: {exc}\nPlease run `rads-toolbox {run_init.name}`.",
            fg="red",
            err=True,
        )
        raise click.Abort() from exc

    context.obj = AppContext(
        project_root=project_root,
        py_project_toml=py_project_toml,
        package_manager=get_package_manager(project_root, py_project_toml),
    )


for command in find_commands(commands.__package__):
    main.add_command(command, command.name)

if __name__ == "__main__":
    main()
