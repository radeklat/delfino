import pytest

from delfino.constants import PackageManager
from delfino.models.pyproject_toml import BuildSystem, PyprojectToml
from delfino.utils import get_package_manager


class TestGetPackageManager:
    @pytest.mark.parametrize(
        "build_system_requires,expected_manager",
        [
            pytest.param(["poetry-core>=1.0.0"], PackageManager.POETRY, id="Poetry with version constraint"),
            pytest.param(["poetry-core>=1.0.0,<2.0"], PackageManager.POETRY, id="Poetry with version range"),
            pytest.param(["poetry-core"], PackageManager.POETRY, id="Poetry without version"),
            pytest.param(["hatchling"], PackageManager.UV, id="UV"),
        ],
    )
    def test_should_identify_package_manager_from_build_system(self, tmp_path, build_system_requires, expected_manager):
        result = get_package_manager(tmp_path, PyprojectToml(build_system=BuildSystem(requires=build_system_requires)))
        assert result == expected_manager

    @pytest.mark.parametrize(
        "file_name,expected_manager",
        [
            pytest.param("poetry.lock", PackageManager.POETRY, id="poetry_lock_file"),
            pytest.param("Pipfile", PackageManager.PIPENV, id="pipfile"),
        ],
    )
    def test_should_fallback_to_file_indicators(self, tmp_path, file_name, expected_manager):
        # GIVEN there is the indicator file
        (tmp_path / file_name).write_text("")

        # AND pyproject.toml without build-system
        pyproject_toml = PyprojectToml()

        # WHEN we check the package manager
        result = get_package_manager(tmp_path, pyproject_toml)

        # THEN it should return the expected package manager
        assert result == expected_manager

    @staticmethod
    def test_should_return_unknown_when_no_indicators(tmp_path):
        # Create pyproject.toml without build-system
        pyproject_toml = PyprojectToml()

        result = get_package_manager(tmp_path, pyproject_toml)

        assert result == PackageManager.UNKNOWN

    @staticmethod
    def test_should_prioritize_file_indicators_over_build_system(tmp_path):
        # GIVEN there is a poetry.lock file (indicates poetry)
        (tmp_path / "poetry.lock").write_text("")

        # AND also build-system with hatchling (indicates uv)
        build_system = BuildSystem(requires=["hatchling"])
        pyproject_toml = PyprojectToml(build_system=build_system)

        # WHEN we check the package manager
        # THEN it should indicate poetry due to the lock file
        assert get_package_manager(tmp_path, pyproject_toml) == PackageManager.POETRY
