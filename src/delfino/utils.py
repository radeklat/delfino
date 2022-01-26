from pathlib import Path
from typing import List, Union

from delfino.constants import PackageManager
from delfino.models.pyproject_toml import Delfino, PyprojectToml

ArgsList = List[Union[str, bytes, Path]]
ArgsType = Union[str, bytes, List]


def get_package_manager(project_root: Path, pyproject_toml: PyprojectToml) -> PackageManager:
    if pyproject_toml.tool.poetry is not None or (project_root / "poetry.lock").exists():
        return PackageManager.POETRY
    if (project_root / "Pipfile").exists() or (project_root / "Pipfile.lock").exists():
        return PackageManager.PIPENV

    return PackageManager.UNKNOWN


def ensure_reports_dir(delfino: Delfino) -> None:
    """Ensures that the reports directory exists."""
    delfino.reports_directory.mkdir(parents=True, exist_ok=True)
