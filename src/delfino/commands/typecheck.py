"""Type checking on source code."""

import click

from delfino.contexts import AppContext, pass_app_context
from delfino.execution import OnError, run
from delfino.terminal_output import print_header
from delfino.utils import ArgsList, ensure_reports_dir
from delfino.validation import assert_pip_package_installed


@click.command()
@click.option("--summary-only", is_flag=True, help="Suppress error messages and show only summary error count.")
@pass_app_context
def typecheck(app_context: AppContext, summary_only: bool):
    """Run type checking on source code.

    A non-zero return code from this task indicates invalid types were discovered.
    """
    assert_pip_package_installed("mypy")

    print_header("RUNNING TYPE CHECKER", icon="🔠")

    delfino = app_context.pyproject_toml.tool.delfino
    reports_file = delfino.reports_directory / "typecheck" / "junit.xml"

    ensure_reports_dir(delfino)

    args: ArgsList = [
        "mypy",
        "--show-column-numbers",
        "--show-error-codes",
        "--color-output",
        "--warn-unused-config",
        "--warn-unused-ignores",
        "--color-output",
        "--follow-imports",
        "silent",
        "--junit-xml",
        reports_file,
        delfino.sources_directory,
        delfino.tests_directory,
    ]

    if summary_only:
        args.extend(["|", "tail", "-n", "1"])

    run(args, env_update_path={"MYPYPATH": delfino.sources_directory}, shell=summary_only, on_error=OnError.ABORT)
