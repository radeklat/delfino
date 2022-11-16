import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from deprecation import DeprecatedWarning
from pydantic import BaseModel, Extra, Field, validator


class Dockerhub(BaseModel):
    build_for_platforms: List[str] = Field(["linux/amd64", "linux/arm64", "linux/arm/v7"], min_items=1)
    username: str


class Typecheck(BaseModel):
    strict_directories: List[Path] = []


class PluginConfig(BaseModel):
    enable_commands: Set[str] = set()
    disable_commands: Set[str] = set()

    @classmethod
    def empty(cls):
        return cls()

    class Config:
        extra = Extra.allow


class Delfino(BaseModel):
    sources_directory: Path = Path("src")
    tests_directory: Path = Path("tests")
    reports_directory: Path = Path("reports")
    test_types: List[str] = ["unit", "integration"]
    disable_commands: Set[str] = Field(default_factory=set)
    verify_commands: Tuple[str, ...] = ("format", "lint", "typecheck", "test-all")
    disable_pre_commit: bool = False
    dockerhub: Optional[Dockerhub] = None
    commands: Dict[str, Any] = Field(default_factory=dict, description="Any additional config given by plugins.")
    disable_plugin_commands: Dict[str, Set[str]] = Field(default_factory=dict)
    plugins: Dict[str, PluginConfig] = Field(default_factory=dict)

    typecheck: Typecheck = Field(default_factory=Typecheck)

    class Config:
        extra = Extra.allow

    @validator("disable_commands")
    @classmethod
    def deprecate_disable_commands(cls, val):
        if val:
            warnings.warn(
                DeprecatedWarning(
                    "tool.delfino.disable_commands configuration",
                    "0.19.0",
                    "1.0.0",
                    "Use tool.delfino.disable_plugin_commands instead.",
                )
            )
        return val


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
