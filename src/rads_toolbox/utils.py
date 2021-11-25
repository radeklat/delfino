from importlib import import_module, resources
from importlib.resources import Package
from pathlib import Path
from typing import Iterator, List, Union

import click

from rads_toolbox.constants import PackageManager
from rads_toolbox.models.pyproject_toml import PyprojectToml, Toolbox

ArgsList = List[Union[str, bytes, Path]]
ArgsType = Union[str, bytes, List]


def get_package_manager(project_root: Path, py_project_toml: PyprojectToml) -> PackageManager:
    if py_project_toml.tool.poetry is not None or (project_root / "poetry.lock").exists():
        return PackageManager.POETRY
    if (project_root / "Pipfile").exists() or (project_root / "Pipfile.lock").exists():
        return PackageManager.PIPENV

    click.secho(
        "Cannot determine package manager used in this project. Only the following ones are supported: "
        + ", ".join(member.value for member in PackageManager.__members__.values()),
        fg="red",
        err=True,
    )
    raise click.Abort()


def ensure_reports_dir(toolbox: Toolbox) -> None:
    """Ensures that the reports directory exists."""
    toolbox.reports_directory.mkdir(parents=True, exist_ok=True)


def command_names(commands: List[click.Command]) -> str:
    return ", ".join(command.name for command in commands if command.name)


def find_commands(package: Package) -> Iterator[click.Command]:
    """Finds all instances of ``click.Command`` in given module.

    Does not traverse modules recursively.
    """
    for filename in resources.contents(package):
        if filename.startswith("_") or not filename.endswith(".py"):
            continue
        plugin = import_module(f"{package}.{filename[:-3]}")
        for obj in vars(plugin).values():
            if isinstance(obj, click.Command):
                yield obj
