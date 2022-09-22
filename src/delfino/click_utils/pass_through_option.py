import shlex
from typing import List

import click


def pass_through_option(command_name: str):
    """Decorator to add an option for pass-through arguments to a click command.

    This will add a `--{command_name}-option` option to the command. The value
    for the option should be passed to the underlying external command, which is
    `command_name`.

    Note, this decorator will not automatically pass the option value to the
    underlying external command. You need to do it manually.

    Example:
    ```
    # Define a command with a pass-through option
    @click.command()
    @pass_through_option("mypy")
    def typecheck(mypy_option: List[str]):
        run(["mypy", *mypy_option])

    # Call the command with a pass-through option
    $ delfino typecheck --mypy-option '--ignore-missing-imports --strict'
    ```

    Args:
        command_name: The name of the command to pass the option value to.

    """
    option_str = f"--{command_name}-option"

    def _split_options(ctx, param, value) -> List[str]:
        del ctx, param
        return shlex.split(value)

    def _pass_through_option(func):
        click.option(
            option_str,
            type=str,
            default="",
            callback=_split_options,
            help=f"Option for {command_name}. Quote multiple options. Example: `{option_str} '--opt --opt-2=val`.",
        )(func)
        return func

    return _pass_through_option
