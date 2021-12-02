from importlib import import_module, resources
from importlib.resources import Package
from typing import Dict, List, Union

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


def _print_help(ctx: click.Context, param: Union[click.Option, click.Parameter], value: bool):
    del param
    if not value or ctx.resilient_parsing:
        return
    click.echo(ctx.get_help())
    ctx.exit()


extended_help_option = click.option(
    "-h",
    "--help",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=_print_help,
    help="Show this message and exit.",
)
"""Adds ``-h`` alongside the built-in ``--help`` option."""
