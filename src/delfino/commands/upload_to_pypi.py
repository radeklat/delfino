"""Type checking on source code."""
import os

import click

from delfino.execution import OnError, run
from delfino.terminal_output import print_header
from delfino.validation import assert_pip_package_installed

_PYPI_API_TOKEN_ENV_VAR = "PYPI_API_TOKEN"


@click.command()
def upload_to_pypi():
    """Upload package to a public Pypi repository.

    Existing versions are skipped.

    Requires `PYPI_API_TOKEN` environment variable to be set to the an upload API token.
    See https://pypi.org/help/#apitoken
    """
    assert_pip_package_installed("twine")

    print_header("Uploading package to Pypi", icon="⬆")

    pypi_api_token = os.getenv("PYPI_API_TOKEN")
    assert pypi_api_token, "The 'PYPI_API_TOKEN' environment variable to authenticate with PyPI is not set."

    if not pypi_api_token.startswith("pypi-"):
        pypi_api_token = f"pypi-{pypi_api_token}"

    run(
        "twine upload --skip-existing --non-interactive dist/*",
        env_update={"TWINE_USERNAME": "__token__", "TWINE_PASSWORD": pypi_api_token},
        on_error=OnError.EXIT,
    )
