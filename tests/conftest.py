import shutil
import subprocess
import sys
import tempfile

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
        try:
            for plugin_dir in FAKE_PLUGINS_DIR.iterdir():
                if not plugin_dir.is_dir():
                    continue
                cmd = f"cd {str(plugin_dir)} && pip install . -q --target "
                cmd += tmpdir
                subprocess.run(cmd, shell=True, check=True)
                shutil.rmtree(plugin_dir / "build")
                shutil.rmtree(plugin_dir / f"{plugin_dir.stem}.egg-info")
            yield
        finally:
            sys.path.remove(tmpdir)
