from pathlib import Path
from typing import Any, Dict, Optional, Set

from pydantic import BaseModel, Extra, Field

from delfino.constants import DEFAULT_LOCAL_COMMANDS_DIRECTORY


class PluginConfig(BaseModel):
    enable_commands: Set[str] = set()
    disable_commands: Set[str] = set()

    @classmethod
    def empty(cls):
        return cls()

    class Config:
        extra = Extra.allow  # Allows arbitrary plugin-specific keys
        orm_mode = True  # Allows `PluginConfigSubclass.from_orm(PluginConfig())`


class Delfino(BaseModel):
    local_commands_directory: Path = DEFAULT_LOCAL_COMMANDS_DIRECTORY
    plugins: Dict[str, PluginConfig] = Field(default_factory=dict)

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
