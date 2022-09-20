import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from _pytest.fixtures import fixture
from click.testing import CliRunner

from tests.constants import PROJECT_ROOT

FAKE_PLUGINS_DIR = PROJECT_ROOT / "tests/integration/fake_plugins"


@fixture(scope="session")
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def install_fake_plugins():
    with tempfile.TemporaryDirectory() as tmpdir:
        sys.path.append(tmpdir)
        # Install the plugin using setuptools
        try:
            # Install the plugin using setuptools
            plugin_dir = FAKE_PLUGINS_DIR / "fake_plugin_a"
            cmd = f"cd {str(plugin_dir)} && pip install . -q --target "
            cmd += tmpdir
            subprocess.run(cmd, shell=True, check=True)
            shutil.rmtree(plugin_dir / "build")
            shutil.rmtree(plugin_dir / f"{plugin_dir.stem}.egg-info")

            # Install the plugin using poetry
            plugin_dir = FAKE_PLUGINS_DIR / "fake_plugin_b"
            wheel_path = Path("dist") / "fake_plugin_b-0.0.1-py2.py3-none-any.whl"
            cmd = f"cd {str(plugin_dir)} && poetry build -q && pip install {str(wheel_path)} -q --target "
            cmd += tmpdir
            subprocess.run(cmd, shell=True, check=True)
            shutil.rmtree(plugin_dir / "dist")
            yield
        finally:
            sys.path.remove(tmpdir)
