from pathlib import Path
from typing import List, Optional

import toml
from pydantic import BaseModel, Extra, Field


class Toolbox(BaseModel):
    source_directory: Optional[Path] = None
    tests_directory: Optional[Path] = None
    reports_directory: Optional[Path] = None
    test_types: List[str] = Field(default_factory=list)


class Poetry(BaseModel):
    name: str
    version: str


class Tool(BaseModel):
    poetry: Optional[Poetry] = None
    toolbox: Optional[Toolbox] = None


class PyProjectToml(BaseModel):
    file_path: Path
    exists: bool
    tool: Optional[Tool] = None

    class Config:
        extra = Extra.allow

    @classmethod
    def load(cls, project_root: Path):
        file_path = project_root / "pyproject.toml"

        try:
            return cls(file_path=file_path, exists=True, **toml.load(file_path))
        except FileNotFoundError:
            return cls(file_path=file_path, exists=False)
