from subprocess import PIPE, CompletedProcess

import click

from delfino.contexts import AppContext, pass_app_context
from delfino.execution import OnError, run
from delfino.terminal_output import print_header, run_command_example
from delfino.validation import assert_pip_package_installed


def _check_result(app_context: AppContext, result: CompletedProcess, check: bool, msg: str):
    if result.returncode == 1 and check:

        msg_lines = [
            f"{msg} before commit. Try following:",
            f" * Run formatter manually with `{run_command_example(run_format, app_context)}` before committing code.",
        ]
        if not app_context.pyproject_toml.tool.delfino.disable_pre_commit:
            msg_lines.insert(1, " * Enable pre-commit hook by running `pre-commit install` in the repository.")

        click.secho(
            "\n".join(msg_lines),
            fg="red",
            err=True,
        )
        raise click.Abort()

    if result.returncode > 1:
        raise click.Abort()


@click.command("format")
@click.option("--check", is_flag=True, help="Only check formatting, don't reformat the code.")
@click.option("--quiet", is_flag=True, help="Don't show progress. Only errors.")
@pass_app_context
def run_format(app_context: AppContext, check: bool, quiet: bool):
    """Runs black code formatter and isort on source code."""
    delfino = app_context.pyproject_toml.tool.delfino

    assert_pip_package_installed("isort")
    assert_pip_package_installed("black")

    if not delfino.disable_pre_commit:
        assert_pip_package_installed("pre-commit")
        # ensure pre-commit is installed
        run("pre-commit install", stdout=PIPE, on_error=OnError.EXIT)

    dirs = [delfino.sources_directory, delfino.tests_directory]
    flags = []

    if check:
        flags.append("--check")

    print_header("Sorting imports", icon="ℹ")

    _check_result(app_context, run(["isort", *dirs, *flags], on_error=OnError.PASS), check, "Import were not sorted")

    print_header("Formatting code", icon="🖤")

    if quiet:
        flags.append("--quiet")

    _check_result(app_context, run(["black", *dirs, *flags], on_error=OnError.PASS), check, "Code was not formatted")
