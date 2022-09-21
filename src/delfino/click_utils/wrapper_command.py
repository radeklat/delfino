from typing import Callable

import click


def wrapper_command(cmd, **attrs) -> Callable:
    def _wrapper_command(func) -> click.Command:
        additional_help = (
            f"This command is a wrapper for `{cmd}` and accept all options for `{cmd}`. "
            f"Please see `{cmd} --help` for more usage."
        )
        attrs["help"] = attrs.get("help", "") + " " + additional_help
        attrs["context_settings"] = {
            **attrs.get("context_settings", {}),
            **dict(ignore_unknown_options=True, allow_extra_args=True),
        }
        _func = click.pass_context(func)
        return click.command(**attrs)(_func)

    return _wrapper_command
