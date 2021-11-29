from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Extra, Field


class Dockerhub(BaseModel):
    build_for_platforms: List[str] = Field(..., min_items=1)
    username: str


class Delfino(BaseModel):
    sources_directory: Path
    tests_directory: Path
    reports_directory: Path
    test_types: List[str]
    disable_commands: Set[str] = Field(default_factory=set)

    dockerhub: Optional[Dockerhub] = None

    plugins: Dict[str, Any] = Field(default_factory=dict, description="Any additional config given by plugins.")

    class Config:
        extra = Extra.allow


class Poetry(BaseModel):
    name: str
    version: str
    scripts: Dict[str, str] = Field(default_factory=dict)
    dependencies: Dict[str, Any] = Field(default_factory=dict)

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
