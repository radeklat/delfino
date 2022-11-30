from pathlib import Path
from typing import List, Union

from delfino.constants import PackageManager
from delfino.models.pyproject_toml import PyprojectToml

ArgsList = List[Union[str, bytes, Path]]
ArgsType = Union[str, bytes, List]


def get_package_manager(project_root: Path, pyproject_toml: PyprojectToml) -> PackageManager:
    if pyproject_toml.tool.poetry is not None or (project_root / "poetry.lock").exists():
        return PackageManager.POETRY
    if (project_root / "Pipfile").exists() or (project_root / "Pipfile.lock").exists():
        return PackageManager.PIPENV

    return PackageManager.UNKNOWN
