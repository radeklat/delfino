from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Extra, Field


class Dockerhub(BaseModel):
    build_for_platforms: List[str] = Field(["linux/amd64", "linux/arm64", "linux/arm/v7"], min_items=1)
    username: str


class Delfino(BaseModel):
    sources_directory: Path = Path("src")
    tests_directory: Path = Path("tests")
    reports_directory: Path = Path("reports")
    test_types: List[str] = ["unit", "integration"]
    disable_commands: Set[str] = Field(default_factory=set)
    verify_commands: Tuple[str, ...] = ("format", "lint", "typecheck", "test-all")
    disable_pre_commit: bool = False
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
    delfino: Delfino = Field(default_factory=Delfino)

    class Config:
        allow_population_by_field_name = True


class PyprojectToml(BaseModel):
    file_path: Optional[Path] = None
    tool: Tool = Field(default_factory=Tool)

    class Config:
        extra = Extra.allow
