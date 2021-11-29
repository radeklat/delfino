from importlib import import_module, resources
from importlib.resources import Package
from pathlib import Path
from typing import Dict, List, Union

import click

from delfino.constants import PackageManager
from delfino.models.pyproject_toml import Delfino, PyprojectToml

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


def ensure_reports_dir(delfino: Delfino) -> None:
    """Ensures that the reports directory exists."""
    delfino.reports_directory.mkdir(parents=True, exist_ok=True)


def command_names(commands: List[click.Command]) -> str:
    return ", ".join(command.name for command in commands if command.name)


def find_commands(package: Package, *, required: bool, new_name: str = "") -> Dict[str, click.Command]:
    """Finds all instances of ``click.Command`` in given module.

    Does not traverse modules recursively.

    Args:
        package: Package to search.
        new_name: If set, ``package`` is a legacy name and ``new_name`` should be used instead.
        required: This package is required.
    """
    try:
        files = resources.contents(package)
    except ModuleNotFoundError:
        if required:
            raise
        return {}

    commands: Dict[str, click.Command] = {}

    for filename in files:
        if filename.startswith("_") or not filename.endswith(".py"):
            continue
        plugin = import_module(f"{package}.{filename[:-3]}")

        for obj in vars(plugin).values():
            if isinstance(obj, click.Command) and obj.name is not None:
                commands[obj.name] = obj

    if commands and new_name:
        click.secho(f"⚠ Plugin module '{package}' is deprecated. Please use '{new_name}' instead.", fg="yellow")

    return commands
