import shlex
from typing import Any, Callable, List

import click

from delfino.contexts import AppContext


def pass_through_command(wrapped_command: str = None, **attrs: Any) -> Callable[[Callable], click.core.Command]:
    """Creates a new command which passes arguments to the wrapped command.

    Commands created by this decorator have `pass_through_args` parameter
    which should be passed to the wrapped command as-is.

    Example:
    ```
    @pass_through_command("pytest")
    def typecheck(pass_through_args: List[str]):
        run(["pytest", *pass_through_args])
    ```

    Note, this decorator will not automatically pass the argument to the wrapped
    command. You need to do it manually.

    The `pass_through_args` parameter can be specified in two ways:

    (1) By `pass_through_args` config in the `pyproject.toml` file.

    This command reads `pass_through_args` config from the config file and set
    the configured value to the `pass_through_args` parameter.

    The config must be placed under; `tool.delfino.plugins.COMMAND_NAME`.

    Example:
    ```
    $ cat pyproject.toml
    ...
    [tool.delfino.plugins.test-unit]
    pass_through_args = '--capture=no'
    ...
    $ delfino test-unit
    -> run `pytest --capture=no`
    ```

    (2) By command line arguments

    Example:
    ```
    $ delfino test-unit path_to_file
    -> run `pytest path_to_file`

    $ delfino test-unit --capture=no
    -> raise error as `--capture` option is not defined

    $ delfino test-unit -- --capture=no # All values after `--` will be considered as arg
    -> run `pytest --capture=no`
    ```

    Args:
        wrapped_command: The name of the command that arguments are passed to. Generates better help message when set.
        attrs: Attributes to pass to click.command().

    """

    def _set_pass_through_args_from_config(ctx, param, value) -> List[str]:
        del param

        # Use command argument when passed.
        # Overwrite config not merge so that config can be disabled when needed.
        if value:
            return value

        app_context: AppContext = ctx.find_object(AppContext)
        command_name: str = ctx.command.name
        pass_through_args_conf: str = app_context.pyproject_toml.tool.delfino.plugins.get(command_name, {}).get(
            "pass_through_args", None
        )
        if pass_through_args_conf:
            return shlex.split(pass_through_args_conf)

        return value

    def _pass_through_command(func) -> click.Command:
        argument_name = "pass_through_args"

        arg_name_in_help = argument_name.upper()
        _wrapped_command = "wrapped command"

        if wrapped_command:
            arg_name_in_help = f"{wrapped_command.upper()}_ARGS"
            _wrapped_command = wrapped_command

        click.argument(
            argument_name,
            metavar=f"[{arg_name_in_help}...]",
            nargs=-1,
            callback=_set_pass_through_args_from_config,
            type=click.UNPROCESSED,
        )(func)
        cmd = click.command(**attrs)(func)
        cmd.help = (
            f"{cmd.help} {arg_name_in_help} are passed to `{_wrapped_command}`."
            f"Use double dash (`--`) to pass options, for example `delfino {cmd.name} -- --some-option`."
        )
        return cmd

    return _pass_through_command
