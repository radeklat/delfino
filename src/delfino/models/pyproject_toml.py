from pathlib import Path
from typing import Any, TypeVar

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
    name: str  # legacy Poetry 1.x field
    version: str  # legacy Poetry 1.x field
    homepage: str | None = None  # legacy Poetry 1.x field
    dependencies: dict[str, Any] = Field(default_factory=dict)  # legacy Poetry 1.x field
    scripts: dict[str, str] = Field(default_factory=dict)  # legacy Poetry 1.x field
    model_config = ConfigDict(extra="allow")


class Uv(BaseModel):
    dev_dependencies: list[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="allow")


class BuildSystem(BaseModel):
    requires: list[str] = Field(default_factory=list)
    build_backend: str | None = None
    model_config = ConfigDict(extra="allow")


class Tool(BaseModel):
    poetry: Poetry | None = None
    uv: Uv | None = None
    delfino: Delfino = Field(default_factory=Delfino)
    model_config = ConfigDict(populate_by_name=True)


class Project(BaseModel):
    name: str | None = None
    version: str | None = None
    homepage: str | None = None
    dependencies: dict[str, Any] | list[str] = Field(default_factory=dict)
    scripts: dict[str, str] = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow")


_Default = TypeVar("_Default")


class PyprojectToml(BaseModel):
    tool: Tool = Field(default_factory=Tool)
    project: Project | None = None
    build_system: BuildSystem | None = None
    model_config = ConfigDict(extra="allow")

    # Convenience properties for accessing common fields with fallbacks to legacy Poetry fields
    def _get_project_attr_with_fallback_to_tool_poetry(self, attr: str, default: _Default) -> Any | _Default:
        if self.project and hasattr(self.project, attr):
            return getattr(self.project, attr)
        if self.tool.poetry and hasattr(self.tool.poetry, attr):
            return getattr(self.tool.poetry, attr)
        return default

    @property
    def project_name(self) -> str | None:
        return self._get_project_attr_with_fallback_to_tool_poetry("name", None)

    @property
    def project_version(self) -> str | None:
        return self._get_project_attr_with_fallback_to_tool_poetry("version", None)

    @property
    def project_homepage(self) -> str | None:
        return self._get_project_attr_with_fallback_to_tool_poetry("homepage", None)

    @property
    def project_scripts(self) -> dict[str, str]:
        return self._get_project_attr_with_fallback_to_tool_poetry("scripts", {})

    @property
    def project_dependencies(self) -> dict[str, Any] | list[str]:
        return self._get_project_attr_with_fallback_to_tool_poetry("dependencies", {})
