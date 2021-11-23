from subprocess import PIPE, CompletedProcess

import click

from rads_toolbox.contexts import AppContext, pass_app_context
from rads_toolbox.utils import OnError, print_header, run, run_command_str


def _check_result(app_context: AppContext, result: CompletedProcess, check: bool, msg: str):
    if result.returncode == 1 and check:
        click.secho(
            f"{msg} before commit. Try following:\n"
            f" * Enable pre-commit hook by running `pre-commit install` in the repository.\n"
            f" * Run formatter manually with `{run_command_str(run_format, app_context)}` before committing code.",
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
    # ensure pre-commit is installed
    run("pre-commit install", stdout=PIPE, on_error=OnError.EXIT)

    toolbox = app_context.py_project_toml.tool.toolbox
    dirs = [toolbox.sources_directory, toolbox.tests_directory]
    flags = []

    if check:
        flags.append("--check")

    print_header("Sorting imports", icon="ℹ")

    _check_result(app_context, run(["isort", *dirs, *flags], on_error=OnError.PASS), check, "Import were not sorted")

    print_header("Formatting code", icon="🖤")

    if quiet:
        flags.append("--quiet")

    _check_result(app_context, run(["black", *dirs, *flags], on_error=OnError.PASS), check, "Code was not formatted")
