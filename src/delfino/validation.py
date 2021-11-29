from delfino.constants import PYPROJECT_TOML_FILENAME
from delfino.execution import pip_package_installed


def pyproject_toml_key_missing(key: str):
    return f"Key '{key}' is missing from the '{PYPROJECT_TOML_FILENAME}' file."


def assert_pip_package_installed(name: str):
    assert pip_package_installed(
        name
    ), f"Optional Python package '{name}' is required by this command but not installed."
