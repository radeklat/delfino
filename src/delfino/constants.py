from enum import Enum

ENTRY_POINT: str = "delfino"
PYPROJECT_TOML_FILENAME = "pyproject.toml"
COMMANDS_DIRECTORY_NAME = "commands"  # deprecated, remove once core package is created


class PackageManager(Enum):
    POETRY = "poetry"
    PIPENV = "pipenv"
    UNKNOWN = "unknown"
