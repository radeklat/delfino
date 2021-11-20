import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml
from click import make_pass_decorator
from invoke import Context


@dataclass
class Project:
    poetry: Dict[str, Any]
    toolbox: Dict[str, Any]
    root_directory: Path

    @property
    def name(self) -> str:
        return self.poetry["name"]

    @property
    def version(self) -> str:
        return self.poetry["version"]

    @property
    def source_directory(self) -> Path:
        return Path(self.toolbox["source_directory"])

    @property
    def tests_directory(self) -> Optional[Path]:
        path = self.toolbox.get("tests_directory", None)
        return None if path is None else Path(path)

    @property
    def test_types(self) -> List[str]:
        return self.toolbox.get("test_types", [])

    @property
    def reports_directory(self) -> Path:
        return Path(self.toolbox["reports_directory"])


class PyProjectToml:
    def __init__(self, project_root: Optional[Path], toolbox_name: str = "toolbox"):
        if not project_root:
            project_root = Path(os.getcwd())

        self._pyproject = toml.load(project_root / "pyproject.toml")
        self._project = Project(self.tool("poetry"), self.tool(toolbox_name), project_root)

    @lru_cache()
    def tool(self, name) -> Dict[str, Any]:
        return self._pyproject["tool"][name]

    @property
    def project(self) -> Project:
        return self._project


@dataclass
class AppContext:
    py_project_toml: PyProjectToml
    ctx: Context


pass_app_context = make_pass_decorator(AppContext)
