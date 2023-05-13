from enum import Enum
from pathlib import Path

ENTRY_POINT: str = "delfino"
PYPROJECT_TOML_FILENAME = "pyproject.toml"
DEFAULT_LOCAL_COMMAND_FOLDERS = (Path("commands"),)


class PackageManager(Enum):
    POETRY = "poetry"
    PIPENV = "pipenv"
    UNKNOWN = "unknown"
