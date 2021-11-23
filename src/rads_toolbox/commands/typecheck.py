"""Type checking on source code."""

import click

from rads_toolbox.contexts import AppContext, pass_app_context
from rads_toolbox.utils import ArgsList, OnError, ensure_reports_dir, print_header, run


@click.command()
@click.option("--summary-only", is_flag=True, help="Suppress error messages and show only summary error count.")
@pass_app_context
def typecheck(app_context: AppContext, summary_only: bool):
    """Run type checking on source code.

    A non-zero return code from this task indicates invalid types were discovered.
    """
    print_header("RUNNING TYPE CHECKER", icon="🔠")

    toolbox = app_context.py_project_toml.tool.toolbox
    reports_file = toolbox.reports_directory / "typecheck" / "junit.xml"

    ensure_reports_dir(toolbox)

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
        toolbox.sources_directory,
        toolbox.tests_directory,
    ]

    if summary_only:
        args.extend(["|", "tail", "-n", "1"])

    run(args, env_update_path={"MYPYPATH": toolbox.sources_directory}, shell=summary_only, on_error=OnError.ABORT)
