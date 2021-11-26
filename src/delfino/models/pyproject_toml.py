from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra, Field


class Delfino(BaseModel):
    sources_directory: Path
    tests_directory: Path
    reports_directory: Path
    test_types: List[str]
    plugins: Dict[str, Any] = Field(default_factory=dict, description="Any additional config given by plugins.")

    class Config:
        extra = Extra.allow


class Poetry(BaseModel):
    name: str
    version: str
    scripts: Optional[Dict[str, str]] = None

    class Config:
        extra = Extra.allow


class Tool(BaseModel):
    poetry: Optional[Poetry] = None
    delfino: Delfino

    class Config:
        allow_population_by_field_name = True


class PyprojectToml(BaseModel):
    file_path: Optional[Path] = None
    tool: Tool

    class Config:
        extra = Extra.allow
