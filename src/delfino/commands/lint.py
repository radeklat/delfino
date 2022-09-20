"""Linting checks on source code."""
import logging
from functools import lru_cache
from itertools import groupby
from pathlib import Path
from subprocess import PIPE
from typing import List, Tuple

import click

from delfino.click_utils.command import command_names
from delfino.click_utils.filepaths import filepaths_argument
from delfino.contexts import AppContext, pass_app_context
from delfino.execution import OnError, run
from delfino.terminal_output import print_header, print_no_issues_found
from delfino.utils import build_target_paths, is_path_relative_to_paths
from delfino.validation import assert_pip_package_installed, pip_package_installed


@click.command()
@filepaths_argument
@pass_app_context
def lint_pydocstyle(app_context: AppContext, filepaths: Tuple[str]):
    """Run docstring linting on source code.

    Docstring linting is done via pydocstyle. The pydocstyle config can be found in the
    `pyproject.toml` file under `[tool.pydocstyle]`. This ensures compliance with PEP 257,
    with a few exceptions. Note that pylint also carries out additional documentation
    style checks.
    """
    assert_pip_package_installed("pydocstyle")

    print_header("documentation style", level=2)
    dirs = build_target_paths(app_context, filepaths, False, False)

    run(["pydocstyle", *dirs], stdout=PIPE, on_error=OnError.ABORT)

    print_no_issues_found()


@click.command()
@filepaths_argument
@pass_app_context
def lint_pycodestyle(app_context: AppContext, filepaths: Tuple[str]):
    """Run PEP8 checking on code.

    PEP8 checking is done via pycodestyle.

    Why pycodestyle and pylint? So far, pylint does not check against every convention in PEP8. As pylint's
    functionality grows, we should move all PEP8 checking to pylint and remove pycodestyle.
    """
    assert_pip_package_installed("pycodestyle")

    print_header("code style (PEP8)", level=2)

    dirs = build_target_paths(app_context, filepaths)

    # TODO(Radek): Implement unofficial config support in pyproject.toml by parsing it
    #  and outputting the result into a supported format?
    #  See:
    #    - https://github.com/PyCQA/pycodestyle/issues/813
    #    - https://github.com/PyCQA/pydocstyle/issues/447
    args = [
        "pycodestyle",
        "--ignore",
        "E501,W503,E231,E203,E402",
        "--exclude",
        ".svn,CVS,.bzr,.hg,.git,__pycache__,.tox,*_config_parser.py",
        *dirs,
    ]
    run(args, stdout=PIPE, on_error=OnError.ABORT)
    # Ignores explained:
    # - E501: Line length is checked by PyLint
    # - W503: Disable checking of "Line break before binary operator". PEP8 recently (~2019) switched to
    #         "line break before the operator" style, so we should permit this usage.
    # - E231: "missing whitespace after ','" is a false positive. Handled by black formatter.

    print_no_issues_found()


def run_pylint(source_dirs: List[Path], pylintrc_folder: Path):
    print_header(", ".join(map(str, source_dirs)), level=3)

    run(
        ["pylint", "-j", str(cpu_count()), "--rcfile", pylintrc_folder / ".pylintrc", *source_dirs],
        stdout=PIPE,
        on_error=OnError.ABORT,
    )

    print_no_issues_found()


@lru_cache(maxsize=1)
def cpu_count():
    log = logging.getLogger("cpu_count")
    fallback_msg = "Number of CPUs could not be determined. Falling back to 1."

    if pip_package_installed("psutil"):
        import psutil  # pylint: disable=import-outside-toplevel

        count = psutil.cpu_count(logical=True)
        if not count:
            log.warning(fallback_msg)
            return 1
        return count

    log.warning(f"`psutil` is not installed. {fallback_msg}")
    return 1


@click.command()
@filepaths_argument
@pass_app_context
def lint_pylint(app_context: AppContext, filepaths: Tuple[str]):
    """Run pylint on code.

    The bulk of our code conventions are enforced via pylint. The pylint config can be
    found in the `.pylintrc` file.
    """
    assert_pip_package_installed("pylint")

    print_header("pylint", level=2)
    delfino = app_context.pyproject_toml.tool.delfino

    def get_pylintrc_folder(path: Path) -> Path:
        if is_path_relative_to_paths(path, [delfino.tests_directory]):
            return delfino.tests_directory
        return app_context.project_root

    target_paths = build_target_paths(app_context, filepaths)
    grouped_paths = groupby(target_paths, get_pylintrc_folder)
    for pylintrc_folder, paths in grouped_paths:
        run_pylint(list(paths), pylintrc_folder)


_COMMANDS = [lint_pylint, lint_pycodestyle, lint_pydocstyle]


@click.command(help=f"Run linting on the entire code base.\n\n" f"Alias for the {command_names(_COMMANDS)} commands.")
@filepaths_argument
@click.pass_context
def lint(click_context: click.Context, filepaths: Tuple[str]):
    print_header("Linting", icon="🔎")
    for command in _COMMANDS:
        click_context.forward(command, filepaths=filepaths)
