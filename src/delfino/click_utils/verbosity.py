import logging
from typing import Union

import click

_NAME_TO_LEVEL = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def _set_log_level(ctx: click.Context, param: Union[click.Option, click.Parameter], value: str):
    del param

    if ctx.resilient_parsing:
        return

    log_level = _NAME_TO_LEVEL.get(value.upper(), logging.INFO)

    logging.basicConfig(level=log_level)
    for logger_name in logging.root.manager.loggerDict:  # pylint: disable=no-member
        logging.getLogger(logger_name).setLevel(log_level)


log_level_option = click.option(
    "--log-level",
    type=click.Choice(list(_NAME_TO_LEVEL.keys()), case_sensitive=False),
    default="INFO",
    is_eager=True,
    show_default=True,
    callback=_set_log_level,
    help="Log level of the output.",
)
