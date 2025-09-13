import toml

from delfino.constants import ENTRY_POINT, PYPROJECT_TOML_FILENAME
from delfino.models.pyproject_toml import PyprojectToml
from tests.constants import PROJECT_ROOT


class TestEntrypointConstant:
    @staticmethod
    def test_should_match_entrypoint_in_pyproject_toml():
        pyproject_toml = PyprojectToml(**toml.load(PROJECT_ROOT / PYPROJECT_TOML_FILENAME))

        assert pyproject_toml.project
        assert ENTRY_POINT in pyproject_toml.project.scripts
