from enum import Enum
from pathlib import Path
from typing import Final, Tuple

ENTRY_POINT: Final[str] = "delfino"
PYPROJECT_TOML_FILENAME: Final[str] = "pyproject.toml"
DEFAULT_LOCAL_COMMAND_FOLDERS: Final[Tuple[Path, ...]] = (Path("commands"),)


class PackageManager(Enum):
    POETRY = "poetry"
    PIPENV = "pipenv"
    UNKNOWN = "unknown"
