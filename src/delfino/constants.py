from enum import Enum

ENTRY_POINT: str = "delfino"
PYPROJECT_TOML_FILENAME = "pyproject.toml"
COMMANDS_DIRECTORY_NAME = "commands"


class PackageManager(Enum):
    POETRY = "poetry"
    PIPENV = "pipenv"
    UNKNOWN = "unknown"
