from pathlib import Path

from click import make_pass_decorator
from invoke import Context
from pydantic import BaseModel

from rads_toolbox.constants import PackageManager
from rads_toolbox.models import external_config, internal_config


class AppContext(BaseModel):
    project_root: Path
    external_py_project_toml: external_config.PyProjectToml
    internal_py_project_toml: internal_config.PyProjectToml
    ctx: Context
    package_manager: PackageManager

    class Config:
        arbitrary_types_allowed = True


pass_app_context = make_pass_decorator(AppContext)
