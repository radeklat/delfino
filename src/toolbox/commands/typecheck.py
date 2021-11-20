"""Type checking on source code."""
import click
import invoke
from termcolor import cprint

from toolbox.constants import AppContext, pass_app_context
from toolbox.utils import ensure_reports_dir, handle_invoke_exceptions, print_header


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
    project = app_context.py_project_toml.project
    reports_dir = project.reports_directory / "typecheck" / "junit.xml"

    ensure_reports_dir(project)

    app_context.ctx.run(
        f"set -o pipefail; "
        f'export MYPYPATH="$MYPYPATH:{project.source_directory}"; '
        f"mypy --show-column-numbers --show-error-codes --color-output --warn-unused-config --warn-unused-ignores "
        f"--follow-imports silent "
        f"--junit-xml {reports_dir} "
        f"{project.source_directory} {project.tests_directory}"
        f"{tail}",
        pty=True,
    )
