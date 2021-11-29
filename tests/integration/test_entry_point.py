import toml

from delfino.constants import ENTRY_POINT, PYPROJECT_TOML_FILENAME
from delfino.models.pyproject_toml import PyprojectToml
from tests.constants import PROJECT_ROOT


class TestEntrypointConstant:
    @staticmethod
    def should_match_entrypoint_in_pyproject_toml():
        file_path = PROJECT_ROOT / PYPROJECT_TOML_FILENAME
        pyproject_toml = PyprojectToml(**toml.load(file_path))
        assert ENTRY_POINT in pyproject_toml.tool.poetry.scripts
