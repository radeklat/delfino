import click

from toolbox.contexts import AppContext, pass_app_context
from toolbox.utils import handle_invoke_exceptions, print_header


@click.command(help="Switches Python venv to a different Python version.")
@click.option("--version", type=str, help="Desired Python version. You can use only MAJOR.MINOR (for example 3.6).")
@pass_app_context
@handle_invoke_exceptions
def switch_python_version(app_context: AppContext, version: str):
    """Use this to test the sub-packages with a different Python version.

    CI pipeline always checks all supported versions automatically.

    Notes:
        This task calls `deactivate` as a precaution for cases when the task is called
        from an active virtual environment.
    """
    print_header(f"Switching to Python {version}", icon="🐍")

    pyenv_python_version = None
    python_versions = sorted(
        (_ for _ in app_context.ctx.run("pyenv versions --bare", hide="stdout").stdout.split("\n") if _),
        key=lambda value: list(map(int, value.split("."))),  # sort numerically
    )

    for python_version in python_versions:
        if python_version.startswith(version):
            pyenv_python_version = python_version
            click.secho(f"✔ Found pyenv Python version '{pyenv_python_version}'.\n", fg="green")

    if not pyenv_python_version:
        available_python_versions = ", ".join(f"'{_}'" for _ in python_versions)
        click.secho(f"❌ No pyenv Python version matching Python {version} found.\n", fg="red")
        print(
            f"Available versions: {available_python_versions}.\n"
            f"See all installable versions with:\n"
            f"\tpyenv install --list\n"
            f"and install it with:\n"
            f"\tpyenv install <PYTHON_VERSION>",
        )
        raise click.Abort()

    app_context.ctx.run(
        f"source deactivate; git clean -fxd .venv && pyenv local {pyenv_python_version} && poetry install",
        pty=True,
    )
