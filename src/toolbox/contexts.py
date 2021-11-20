from dataclasses import dataclass
from pathlib import Path

from click import make_pass_decorator
from invoke import Context

from toolbox.config import PyProjectToml


@dataclass
class AppContext:
    project_root: Path
    py_project_toml: PyProjectToml
    ctx: Context


pass_app_context = make_pass_decorator(AppContext)
