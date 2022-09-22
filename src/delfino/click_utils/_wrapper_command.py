from typing import Callable

import click


def wrapper_command(command_name, **attrs) -> Callable:
    """An utility decorator to create a click.Command which wraps another command.

    *It captures undefined options/arguments.*
    Captured options/arguments can be accessed through the `args` attribute of
    the context object. Captured undefined options/arguments must be passed to
    the wrapped command.

    The wrapper command will not *automatically* pass captured undefined
    options/arguments to the wrapped command. This must be done manually.

    Example:
    ```
    @wrapper_command("mypy")
    def test(click_context: click.Context):
        run(["mypy", *click_context.args])

    # You can still add your own options.
    @wrapper_command("mypy")
    @click.option('--hoge', is_flag=True)
    def test(click_context: click.Context, hoge: bool):
        print(hoge)
        run(["mypy", *click_context.args])

    # Should carefully be used with `click.argument()`.
    @wrapper_command("mypy")
    @click.argument('params', nargs=-1)
    def test(click_context: click.Context, params: list):
        # params eat up all undefined options/arguments and click.context.args is empty.
    ```

    *Add help message to tell users that this is a wrapper command.*
    This is helpful as the help message for the wrapper command doesn't show
    options for the wrapped command.

    Args:
        command_name (str): The name of the wrapped command. Used in help message.
        attrs (dict): Optional attributes passed to the click.command.
    Returns:
        Callable: A decorator to create a click.Command which wraps another command.
    """

    def _wrapper_command(func) -> click.Command:
        additional_help = (
            f"This command is a wrapper for `{command_name}`. Options not on this help will be directly passed through to `{command_name}`. Some options may not be applied when the command has fix default value."
            f"Check `{command_name} --help` for available options."
        )
        attrs["help"] = attrs.get("help", "") + " " + additional_help
        attrs["context_settings"] = {
            **attrs.get("context_settings", {}),
            **dict(ignore_unknown_options=True, allow_extra_args=True),
        }
        _func = click.pass_context(func)
        return click.command(**attrs)(_func)

    return _wrapper_command
