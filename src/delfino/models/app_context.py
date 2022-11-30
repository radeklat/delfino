from pathlib import Path

from pydantic import BaseModel

from delfino.constants import PackageManager
from delfino.models.pyproject_toml import PluginConfig, PyprojectToml


class AppContext(BaseModel):
    project_root: Path
    pyproject_toml: PyprojectToml
    package_manager: PackageManager
    plugin_config: PluginConfig

    class Config:
        arbitrary_types_allowed = True
