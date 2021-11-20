from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Extra, Field


class Toolbox(BaseModel):
    sources_directory: Path
    tests_directory: Path
    reports_directory: Path
    test_types: List[str]


class Poetry(BaseModel):
    name: str
    version: str


class Tool(BaseModel):
    poetry: Optional[Poetry] = None
    toolbox: Toolbox


class PyProjectToml(BaseModel):
    file_path: Path
    tool: Tool = Field(default_factory=Tool)

    class Config:
        extra = Extra.allow
