from pathlib import Path
from typing import List, Tuple, Union

from delfino.constants import PackageManager
from delfino.contexts import AppContext
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


def build_target_paths(
    app_context: AppContext, filepaths: Tuple[str] = None, include_tests: bool = True, include_commands: bool = True
) -> List[Path]:
    if filepaths:
        return [Path(path) for path in filepaths]
    delfino = app_context.pyproject_toml.tool.delfino
    target_paths: List[Path] = [delfino.sources_directory]
    if include_tests and delfino.tests_directory.exists():
        target_paths.append(delfino.tests_directory)
    if include_commands and app_context.commands_directory.exists():
        target_paths.append(app_context.commands_directory)
    return target_paths


def _is_path_relative_to_paths(path: Path, paths: List[Path]) -> bool:
    for _path in paths:
        try:
            path.relative_to(_path)
            return True
        except ValueError:
            continue
    return False
