from enum import Enum

ENTRY_POINT: str = "rads-toolbox"


class PackageManager(Enum):
    POETRY = "poetry"
    PIPENV = "pipenv"
