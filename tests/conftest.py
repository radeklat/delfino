from pathlib import Path

import pytest
import toml
from click.testing import CliRunner

from delfino.constants import PYPROJECT_TOML_FILENAME
from delfino.models.app_context import AppContext
from delfino.models.pyproject_toml import PluginConfig, PyprojectToml
from delfino.utils import get_package_manager


@pytest.fixture(scope="session")
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def project_root():
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def pyproject_toml(project_root):
    return PyprojectToml(**toml.load(project_root / PYPROJECT_TOML_FILENAME))


@pytest.fixture()
def context_obj(project_root, pyproject_toml):
    return AppContext(
        project_root=project_root,
        pyproject_toml=pyproject_toml,
        package_manager=get_package_manager(project_root, pyproject_toml),
        plugin_config=PluginConfig.empty(),
    )
