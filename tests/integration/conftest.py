import shutil
import subprocess
import sys
import tempfile

import pytest

from tests.constants import PROJECT_ROOT

FAKE_PLUGINS_DIR = PROJECT_ROOT / "tests/integration/fake_plugins"


def _build_and_install_setuptools_plugin(tmpdir, plugin_name: str):
    plugin_dir = FAKE_PLUGINS_DIR / plugin_name
    cmd = f"cd {plugin_dir} && pip install . -q --target {tmpdir}"
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(plugin_dir / "build")
    shutil.rmtree(plugin_dir / f"{plugin_dir.stem}.egg-info")


def _build_and_install_poetry_plugin(tmpdir, plugin_name: str):
    plugin_dir = FAKE_PLUGINS_DIR / plugin_name
    wheel_path = plugin_dir / "dist" / f"{plugin_name}-0.0.1-py2.py3-none-any.whl"
    subprocess.run(f"cd {plugin_dir} && poetry build -q", shell=True, check=True)
    subprocess.run(f"pip install {wheel_path} -q --target {tmpdir}", shell=True, check=True)
    shutil.rmtree(plugin_dir / "dist")


@pytest.fixture(scope="session")
def install_fake_plugins():
    with tempfile.TemporaryDirectory() as tmpdir:
        sys.path.append(tmpdir)
        try:
            _build_and_install_setuptools_plugin(tmpdir, "fake_plugin_a")
            for plugin_name in [
                "fake_plugin_b",
                "fake_plugin_init_only",
                "fake_plugin_without_entry_point",
                "fake_plugin_with_different_entry_point",
            ]:
                _build_and_install_poetry_plugin(tmpdir, plugin_name)
            yield
        finally:
            sys.path.remove(tmpdir)
