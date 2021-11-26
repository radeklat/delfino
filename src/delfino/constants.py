from enum import Enum

ENTRY_POINT: str = "delfino"
PYPROJECT_TOML = "pyproject.toml"


class PackageManager(Enum):
    POETRY = "poetry"
    PIPENV = "pipenv"
