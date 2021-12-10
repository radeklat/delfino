import sys
from subprocess import PIPE

from delfino.constants import PYPROJECT_TOML_FILENAME
from delfino.execution import OnError, run

if sys.version_info <= (3, 8):
    import importlib_metadata as metadata
else:
    from importlib import metadata


def pyproject_toml_key_missing(key: str):
    return f"Key '{key}' is missing from the '{PYPROJECT_TOML_FILENAME}' file."


def pip_package_installed(name: str, sub_process: bool = False) -> bool:
    if sub_process:
        return run(f"pip show -q {name}", stdout=PIPE, stderr=PIPE, on_error=OnError.PASS, shell=True).returncode == 0

    try:
        metadata.Distribution.from_name(name)
    except metadata.PackageNotFoundError:
        return False

    return True


def assert_pip_package_installed(name: str, required_by: str = "this command"):
    assert pip_package_installed(
        name
    ), f"Optional Python package '{name}' is required by {required_by} but not installed."
