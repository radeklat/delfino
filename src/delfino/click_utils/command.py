from importlib import import_module, resources
from importlib.resources import Package
from typing import Dict, List, cast

import click


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
    except ModuleNotFoundError as exc:
        if required or f"'{package}'" not in str(exc):
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


def get_root_command(click_context: click.Context) -> click.MultiCommand:
    """Find the root command.

    In the context of `delfino`, this is generally the ``main.Commands`` instance.
    """
    while click_context.parent:
        click_context = click_context.parent
    return cast(click.MultiCommand, click_context.command)
