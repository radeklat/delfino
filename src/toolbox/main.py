from pathlib import Path
from typing import Optional

import click
from invoke import Context as InvokeContext

from toolbox.commands.format import run_format
from toolbox.commands.lint import lint, lint_pycodestyle, lint_pydocstyle, lint_pylint
from toolbox.commands.switch_python_version import switch_python_version
from toolbox.commands.test import coverage_open, coverage_report, test_all, test_integration, test_unit
from toolbox.commands.typecheck import typecheck
from toolbox.commands.verify_all import verify_all
from toolbox.constants import AppContext, PyProjectToml


@click.group()
@click.option(
    "--project-root",
    default=None,
    type=click.Path(exists=True, dir_okay=True, file_okay=False, readable=True, writable=True),
    help="Root folder of the project, if not running from it.",
)
def main(project_root: Optional[Path] = None):
    click.get_current_context().obj = AppContext(
        py_project_toml=PyProjectToml(project_root=project_root),
        ctx=InvokeContext(),
    )


_COMMANDS = [
    run_format,
    typecheck,
    lint_pydocstyle,
    lint_pycodestyle,
    lint_pylint,
    lint,
    test_unit,
    test_integration,
    coverage_report,
    test_all,
    coverage_open,
    switch_python_version,
    verify_all,
]

for command in _COMMANDS:
    main.add_command(command, command.name)

if __name__ == "__main__":
    main()
