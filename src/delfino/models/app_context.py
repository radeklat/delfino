from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from delfino.constants import PackageManager
from delfino.models.pyproject_toml import PluginConfig, PyprojectToml

PluginConfigType = TypeVar("PluginConfigType", bound=PluginConfig)


class AppContext(BaseModel, Generic[PluginConfigType]):
    project_root: Path
    pyproject_toml: PyprojectToml
    package_manager: PackageManager
    plugin_config: PluginConfigType
    model_config = ConfigDict(arbitrary_types_allowed=True)
