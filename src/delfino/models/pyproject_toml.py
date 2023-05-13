from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from warnings import warn

from pydantic import BaseModel, Extra, Field

from delfino.constants import DEFAULT_LOCAL_COMMAND_FOLDERS


class PluginConfig(BaseModel):
    enable_commands: Set[str] = Field(default_factory=set)
    disable_commands: Set[str] = Field(default_factory=set)
    command_groups: Dict[str, List[str]] = Field(default_factory=dict)

    @classmethod
    def empty(cls):
        return cls()

    class Config:
        extra = Extra.allow  # Allows arbitrary plugin-specific keys


class Delfino(BaseModel):
    local_command_folders: Tuple[Path, ...] = DEFAULT_LOCAL_COMMAND_FOLDERS
    plugins: Dict[str, PluginConfig] = Field(default_factory=dict)
    command_groups: Dict[str, List[str]] = Field(default_factory=dict)

    @property
    def local_commands_directory(self) -> Path:
        warn(
            "tool.delfino.local_commands_directory is deprecated. Use tool.delfino.local_command_folders instead.",
            DeprecationWarning,
        )
        return self.local_command_folders[0]

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
    tool: Tool = Field(default_factory=Tool)

    class Config:
        extra = Extra.allow
