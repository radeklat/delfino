from pathlib import Path
from typing import List

import toml
from pydantic import ValidationError

from delfino.constants import PYPROJECT_TOML_FILENAME
from delfino.models import PyprojectToml

_RC_FILE_NAME = ".delfinorc"


class ConfigValidationError(ValueError):
    pass


def _rc_locations(project_root: Path) -> List[Path]:  # pragma: no cover
    return [
        Path.home() / _RC_FILE_NAME,
        project_root / PYPROJECT_TOML_FILENAME,
        project_root / _RC_FILE_NAME,
    ]


def load_config(project_root: Path) -> PyprojectToml:
    """Loads a config with defined precedence.

    Looks up the following locations in this order (later overwrite earlier):
        - $USER/.delfinorc
        - <project_root>/pyproject.toml
        - <project_root>/.delfinorc

    The ``.delfinorc`` files have the same TOML format and structure as the
    ``pyproject.toml`` file.

    Args:
        project_root: Root of the project.
    """
    pyproject_toml = PyprojectToml()

    for rc_file in _rc_locations(project_root):
        if not rc_file.is_file():
            continue
        try:
            pyproject_toml = PyprojectToml(**toml.load(rc_file))
        except ValidationError as exc:
            raise ConfigValidationError(f"Delfino appears to be misconfigured in '{rc_file}': {exc}") from exc

    return pyproject_toml
