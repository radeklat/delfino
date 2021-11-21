import os
from pathlib import Path
from typing import Optional

import click
import toml
from invoke import Context as InvokeContext
from pydantic import ValidationError

from rads_toolbox.commands.format import run_format
from rads_toolbox.commands.init import run_init
from rads_toolbox.commands.lint import lint, lint_pycodestyle, lint_pydocstyle, lint_pylint
from rads_toolbox.commands.switch_python_version import switch_python_version
from rads_toolbox.commands.test import coverage_open, coverage_report, test_all, test_integration, test_unit
from rads_toolbox.commands.typecheck import typecheck
from rads_toolbox.commands.verify_all import verify_all
from rads_toolbox.contexts import AppContext
from rads_toolbox.models import external_config, internal_config
from rads_toolbox.utils import get_package_manager


@click.group()
@click.option(
    "--project-root",
    default=None,
    type=click.Path(exists=True, dir_okay=True, file_okay=False, readable=True, writable=True),
    help="Root folder of the project, if not running from it.",
)
def main(project_root: Optional[Path] = None):
    if not project_root:
        project_root = Path(os.getcwd())

    filename = "pyproject.toml"
    file_path = (project_root / filename).relative_to(project_root)
    context = click.get_current_context()

    if context.invoked_subcommand == run_init.name:
        context.obj = file_path
        return

    int_py_project_toml = internal_config.PyProjectToml(**toml.load(Path(__file__).parent.parent.parent / filename))

    try:
        ext_py_project_toml = external_config.PyProjectToml(file_path=file_path, **toml.load(file_path))
    except (FileNotFoundError, ValidationError) as exc:
        click.secho(
            f"Toolbox appears to be misconfigured: {exc}\nPlease run `rads-toolbox {run_init.name}`.",
            fg="red",
            err=True,
        )
        raise click.Abort() from exc

    context.obj = AppContext(
        project_root=project_root,
        external_py_project_toml=ext_py_project_toml,
        internal_py_project_toml=int_py_project_toml,
        ctx=InvokeContext(),
        package_manager=get_package_manager(project_root, ext_py_project_toml),
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
    run_init,
]

for command in _COMMANDS:
    main.add_command(command, command.name)

if __name__ == "__main__":
    main()
