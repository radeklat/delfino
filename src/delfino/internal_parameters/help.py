from typing import Union

import click


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
