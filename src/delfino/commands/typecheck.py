"""Type checking on source code."""

from itertools import groupby
from pathlib import Path
from typing import List, Tuple

import click

from delfino.click_utils.filepaths import filepaths_argument
from delfino.contexts import AppContext, pass_app_context
from delfino.execution import OnError, run
from delfino.terminal_output import print_header
from delfino.utils import ArgsList, ensure_reports_dir
from delfino.validation import assert_pip_package_installed


def _run_typecheck(paths: List[Path], strict: bool, reports_file: Path, summary_only: bool, mypypath: Path):
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

    args.extend(paths)

    if summary_only:
        args.extend(["|", "tail", "-n", "1"])

    run(args, env_update_path={"MYPYPATH": mypypath}, on_error=OnError.ABORT)


def is_path_relative_to_paths(path: Path, paths: List[Path]) -> bool:
    for _path in paths:
        try:
            path.relative_to(_path)
            return True
        except ValueError:
            continue
    return False


@click.command()
@click.option("--summary-only", is_flag=True, help="Suppress error messages and show only summary error count.")
@filepaths_argument
@pass_app_context
def typecheck(app_context: AppContext, summary_only: bool, filepaths: Tuple[str]):
    """Run type checking on source code.

    A non-zero return code from this task indicates invalid types were discovered.
    """
    assert_pip_package_installed("mypy")

    print_header("RUNNING TYPE CHECKER", icon="🔠")

    delfino = app_context.pyproject_toml.tool.delfino
    ensure_reports_dir(delfino)

    target_paths: List[Path] = []
    if filepaths:
        target_paths = [Path(path) for path in filepaths]
    else:
        target_paths = [delfino.sources_directory, delfino.tests_directory]
        if app_context.commands_directory.exists():
            target_paths.append(app_context.commands_directory)

    strict_paths = delfino.typecheck.strict_directories
    grouped_paths = groupby(target_paths, lambda current_path: is_path_relative_to_paths(current_path, strict_paths))

    for force_typing, group in grouped_paths:
        report_filepath = (
            delfino.reports_directory / "typecheck" / f"junit-{'strict' if force_typing else 'nonstrict'}.xml"
        )
        _run_typecheck(list(group), force_typing, report_filepath, summary_only, delfino.sources_directory)
