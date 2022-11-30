import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from delfino.constants import DEFAULT_LOCAL_COMMANDS_DIRECTORY
from delfino.models.pyproject_toml import PluginConfig

ALL_PLUGINS_ALL_COMMANDS = {
    "fake-plugin-a": PluginConfig.empty(),
    "fake-plugin-b": PluginConfig.empty(),
    "fake-plugin-init-only": PluginConfig.empty(),
}


@contextmanager
def demo_command(folder_name: Path = DEFAULT_LOCAL_COMMANDS_DIRECTORY, file_name: str = "demo.py") -> Iterator[str]:
    command_name = "demo"

    with tempfile.TemporaryDirectory() as tmpdir:
        root_dir = tmpdir / folder_name
        root_dir.mkdir(exist_ok=True)
        (root_dir / "__init__.py").touch()
        (root_dir / file_name).write_text(f"import click\n@click.command()\ndef {command_name}():\n    pass\n")
        sys.path.append(tmpdir)
        try:
            yield command_name
        finally:
            sys.path.pop()
