from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, ConfigDict, Field

from delfino.constants import DEFAULT_LOCAL_COMMAND_FOLDERS


class PluginConfig(BaseModel):
    enable_commands: Set[str] = Field(default_factory=set)
    disable_commands: Set[str] = Field(default_factory=set)
    command_groups: Dict[str, List[str]] = Field(default_factory=dict)

    @classmethod
    def empty(cls):
        return cls()

    model_config = ConfigDict(extra="allow")


class Delfino(BaseModel):
    local_command_folders: Tuple[Path, ...] = DEFAULT_LOCAL_COMMAND_FOLDERS
    plugins: Dict[str, PluginConfig] = Field(default_factory=dict)
    command_groups: Dict[str, List[str]] = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow")


class Poetry(BaseModel):
    name: str
    version: str
    scripts: Dict[str, str] = Field(default_factory=dict)
    dependencies: Dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow")


class Tool(BaseModel):
    poetry: Optional[Poetry] = None
    delfino: Delfino = Field(default_factory=Delfino)
    model_config = ConfigDict(populate_by_name=True)


class PyprojectToml(BaseModel):
    tool: Tool = Field(default_factory=Tool)
    model_config = ConfigDict(extra="allow")
