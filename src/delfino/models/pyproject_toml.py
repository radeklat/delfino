from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from delfino.constants import DEFAULT_LOCAL_COMMAND_FOLDERS


class PluginConfig(BaseModel):
    enable_commands: set[str] = Field(default_factory=set)
    disable_commands: set[str] = Field(default_factory=set)
    command_groups: dict[str, list[str]] = Field(default_factory=dict)

    @classmethod
    def empty(cls):
        return cls()

    model_config = ConfigDict(extra="allow")


class Delfino(BaseModel):
    local_command_folders: tuple[Path, ...] = DEFAULT_LOCAL_COMMAND_FOLDERS
    plugins: dict[str, PluginConfig] = Field(default_factory=dict)
    command_groups: dict[str, list[str]] = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow")


class Poetry(BaseModel):
    name: str
    version: str
    scripts: dict[str, str] = Field(default_factory=dict)
    dependencies: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow")


class BuildSystem(BaseModel):
    requires: list[str] = Field(default_factory=list)
    build_backend: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class Tool(BaseModel):
    poetry: Optional[Poetry] = None
    uv: Optional[dict[str, Any]] = None
    delfino: Delfino = Field(default_factory=Delfino)
    model_config = ConfigDict(populate_by_name=True)


class Project(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    dependencies: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow")


class PyprojectToml(BaseModel):
    tool: Tool = Field(default_factory=Tool)
    project: Optional[Project] = None
    build_system: Optional[BuildSystem] = None
    model_config = ConfigDict(extra="allow")
