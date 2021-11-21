from pathlib import Path

from click import make_pass_decorator
from invoke import Context
from pydantic import BaseModel

from rads_toolbox.config import PyProjectToml


class AppContext(BaseModel):
    project_root: Path
    py_project_toml: PyProjectToml
    ctx: Context

    class Config:
        arbitrary_types_allowed = True


pass_app_context = make_pass_decorator(AppContext)
