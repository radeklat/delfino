from pathlib import Path

from click import make_pass_decorator
from invoke import Context
from pydantic import BaseModel

from rads_toolbox.constants import PackageManager
from rads_toolbox.models.pyproject_toml import PyprojectToml


class AppContext(BaseModel):
    project_root: Path
    py_project_toml: PyprojectToml
    ctx: Context
    package_manager: PackageManager

    class Config:
        arbitrary_types_allowed = True


pass_app_context = make_pass_decorator(AppContext)
