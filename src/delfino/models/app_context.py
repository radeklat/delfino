from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

from delfino.constants import PackageManager
from delfino.models.pyproject_toml import PluginConfig, PyprojectToml

PluginConfigType = TypeVar("PluginConfigType", bound=PluginConfig)


class AppContext(Generic[PluginConfigType], BaseModel):
    project_root: Path
    pyproject_toml: PyprojectToml
    package_manager: PackageManager
    plugin_config: PluginConfigType

    class Config:
        arbitrary_types_allowed = True
