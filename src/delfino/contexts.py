from pathlib import Path

from click import make_pass_decorator
from pydantic import BaseModel

from delfino.constants import COMMANDS_DIRECTORY_NAME, PackageManager
from delfino.models.pyproject_toml import PyprojectToml


class AppContext(BaseModel):
    project_root: Path
    pyproject_toml: PyprojectToml
    package_manager: PackageManager
    commands_directory: Path = Path(COMMANDS_DIRECTORY_NAME)

    class Config:
        arbitrary_types_allowed = True


pass_app_context = make_pass_decorator(AppContext)
