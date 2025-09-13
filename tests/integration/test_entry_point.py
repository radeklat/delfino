import toml

from delfino.constants import ENTRY_POINT, PYPROJECT_TOML_FILENAME
from delfino.models.pyproject_toml import PyprojectToml
from tests.constants import PROJECT_ROOT


class TestEntrypointConstant:
    @staticmethod
    def test_should_match_entrypoint_in_pyproject_toml():
        file_path = PROJECT_ROOT / PYPROJECT_TOML_FILENAME
        pyproject_toml = PyprojectToml(**toml.load(file_path))

        # Check that we have either Poetry or uv format
        assert pyproject_toml.tool.poetry is not None or pyproject_toml.tool.uv is not None

        # Check that the entry point exists in scripts
        scripts = pyproject_toml.project_scripts
        assert ENTRY_POINT in scripts
