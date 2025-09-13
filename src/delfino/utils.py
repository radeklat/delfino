from pathlib import Path

from delfino.constants import PackageManager
from delfino.models.pyproject_toml import PyprojectToml

ArgsList = list[str | bytes | Path]
ArgsType = str | bytes | list


def get_package_manager(project_root: Path, pyproject_toml: PyprojectToml) -> PackageManager:
    # Check build-system requires for poetry and uv
    if pyproject_toml.tool.poetry is not None or (project_root / "poetry.lock").exists():
        return PackageManager.POETRY

    if pyproject_toml.tool.uv is not None or (project_root / "uv.lock").exists():
        return PackageManager.UV

    if pyproject_toml.build_system and pyproject_toml.build_system.requires:
        requires = pyproject_toml.build_system.requires
        if any("poetry" in req for req in requires):
            return PackageManager.POETRY
        if any("hatchling" in req for req in requires):
            return PackageManager.UV

    if (project_root / "Pipfile").exists() or (project_root / "Pipfile.lock").exists():
        return PackageManager.PIPENV

    return PackageManager.UNKNOWN
