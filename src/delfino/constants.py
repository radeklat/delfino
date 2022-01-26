from enum import Enum

ENTRY_POINT: str = "delfino"
PYPROJECT_TOML_FILENAME = "pyproject.toml"


class PackageManager(Enum):
    POETRY = "poetry"
    PIPENV = "pipenv"
    UNKNOWN = "unknown"
