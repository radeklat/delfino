"""Type checking on source code."""
import click
import invoke
from termcolor import cprint

from rads_toolbox.contexts import AppContext, pass_app_context
from rads_toolbox.utils import ensure_reports_dir, handle_invoke_exceptions, print_header


def _handle_unexpected_pass(expected_to_fail: bool, result: invoke.Result, path: str):
    if expected_to_fail and not result.failed:
        result.exited = 1  # force failure
        cprint(
            f"\nThis folder was expected to fail but no errors were found.\n\nPlease edit the "
            f"'{__file__}' file and move '{path}' from `broken_directories` to `fixed_directories`.",
            "red",
            attrs=["bold"],
        )


@click.command()
@click.option("--summary-only", is_flag=True, help="Suppress error messages and show only summary error count.")
@pass_app_context
@handle_invoke_exceptions
def typecheck(app_context: AppContext, summary_only: bool):
    """Run type checking on source code.

    A non-zero return code from this task indicates invalid types were discovered.
    """
    print_header("RUNNING TYPE CHECKER")

    tail = " | tail -n 1" if summary_only else ""
    toolbox = app_context.external_py_project_toml.tool.toolbox
    reports_dir = toolbox.reports_directory / "typecheck" / "junit.xml"

    ensure_reports_dir(toolbox)

    app_context.ctx.run(
        f"set -o pipefail; "
        f'export MYPYPATH="$MYPYPATH:{toolbox.sources_directory}"; '
        f"mypy --show-column-numbers --show-error-codes --color-output --warn-unused-config --warn-unused-ignores "
        f"--follow-imports silent "
        f"--junit-xml {reports_dir} "
        f"{toolbox.sources_directory} {toolbox.tests_directory}"
        f"{tail}",
        pty=True,
    )
