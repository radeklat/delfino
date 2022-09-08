"""Type checking on source code."""

from typing import List

import click

from delfino.contexts import AppContext, pass_app_context
from delfino.execution import OnError, run
from delfino.terminal_output import print_header
from delfino.utils import ArgsList, ensure_reports_dir
from delfino.validation import assert_pip_package_installed


@click.command()
@click.option("--summary-only", is_flag=True, help="Suppress error messages and show only summary error count.")
@click.option("--path", "-p", multiple=True, default=[], help="Directory/File paths to type check.")
@click.option("--strict", "-s", default=False, is_flag=True, show_default=True, help="Add --strict flag to mypy.")
@pass_app_context
def typecheck(app_context: AppContext, summary_only: bool, path: List[str], strict: bool):
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
        "--allow-untyped-decorators",
        "--follow-imports",
        "silent",
        "--junit-xml",
        reports_file,
    ]
    if strict:
        args.append("--strict")

    _path: ArgsList = list(path) or [delfino.sources_directory, delfino.tests_directory]
    args.extend(_path)

    if app_context.commands_directory.exists():
        args.append(app_context.commands_directory)

    if summary_only:
        args.extend(["|", "tail", "-n", "1"])

    run(args, env_update_path={"MYPYPATH": delfino.sources_directory}, shell=summary_only, on_error=OnError.ABORT)
