from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Extra, Field


class Toolbox(BaseModel):
    sources_directory: Path
    tests_directory: Path
    reports_directory: Path
    test_types: List[str]


class Poetry(BaseModel):
    name: str
    version: str
    scripts: Optional[Dict[str, str]] = None


class Tool(BaseModel):
    poetry: Optional[Poetry] = None
    toolbox: Toolbox = Field(..., alias="rads_toolbox")

    class Config:
        allow_population_by_field_name = True


class PyprojectToml(BaseModel):
    file_path: Optional[Path] = None
    tool: Tool

    class Config:
        extra = Extra.allow
