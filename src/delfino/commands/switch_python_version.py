from pathlib import Path
from subprocess import PIPE

import click

from delfino.constants import PackageManager
from delfino.contexts import AppContext, pass_app_context
from delfino.execution import OnError, run
from delfino.terminal_output import print_header
from delfino.validation import assert_package_manager_is_known, pip_package_installed


@click.command()
@click.argument("version", type=str)
@pass_app_context
def switch_python_version(app_context: AppContext, version: str):
    """Switches Python venv to a different Python version.

    - VERSION: Desired Python version. You can use only MAJOR.MINOR (for example 3.6).

    Use this to test the sub-packages with a different Python version. CI pipeline always
    checks all supported versions automatically.

    Notes:
        This task calls `deactivate` as a precaution for cases when the task is called
        from an active virtual environment.
    """
    print_header(f"Switching to Python {version}", icon="🐍")

    pyenv_python_version = None
    python_versions = sorted(
        (_ for _ in run("pyenv versions --bare", stdout=PIPE, on_error=OnError.EXIT).stdout.decode().split("\n") if _),
        key=lambda value: list(map(int, value.split("."))),  # sort numerically
    )

    assert Path(".venv").exists(), "Folder '.venv'."

    for python_version in python_versions:
        if python_version.startswith(version):
            pyenv_python_version = python_version
            click.secho(f"✔ Found pyenv Python version '{pyenv_python_version}'.", fg="green")

    if not pyenv_python_version:
        available_python_versions = ", ".join(f"'{_}'" for _ in python_versions)
        click.secho(f"❌ No pyenv Python version matching Python {version} found.", fg="red")
        print(
            f"Available versions: {available_python_versions}.\n"
            f"See all installable versions with:\n"
            f"\tpyenv install --list\n"
            f"and install it with:\n"
            f"\tpyenv install <PYTHON_VERSION>",
        )
        raise click.Abort()

    package_manager = app_context.package_manager
    assert_package_manager_is_known(package_manager)
    if package_manager == PackageManager.POETRY:
        install_command = "poetry install --no-root"
    elif package_manager == PackageManager.PIPENV:
        install_command = "pipenv install -d --deploy"
    else:
        click.secho("No compatible package manager detected. Skipping package installation.", fg="red", err=True)
        raise click.Abort()

    click.secho("ℹ Removing current virtualenv ...", fg="blue")
    run("git clean -fxd .venv", stdout=PIPE, stderr=PIPE, on_error=OnError.EXIT)

    click.secho(f"ℹ Switching to Python {pyenv_python_version} ...", fg="blue")
    run(["pyenv", "local", pyenv_python_version], stdout=PIPE, stderr=PIPE, on_error=OnError.EXIT)

    click.secho(f"✔ Detected {package_manager.value.capitalize()} package manager.", fg="green")

    if not pip_package_installed(package_manager.value, sub_process=True):
        click.secho(f"⚠ {package_manager.value.capitalize()} is not installed. Installing ...", fg="yellow")
        run(f"pip install {package_manager.value}", stdout=PIPE, stderr=PIPE, on_error=OnError.EXIT)
    else:
        click.secho(f"✔ {package_manager.value.capitalize()} is installed.", fg="green")

    run(install_command, on_error=OnError.EXIT)
