from enum import Enum

ENTRY_POINT: str = "rads-toolbox"
PYPROJECT_TOML = "pyproject.toml"


class PackageManager(Enum):
    POETRY = "poetry"
    PIPENV = "pipenv"
