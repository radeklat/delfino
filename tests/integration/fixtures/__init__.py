import sys
import tempfile
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path

from pydantic import BaseModel

from delfino.constants import DEFAULT_LOCAL_COMMAND_FOLDERS
from delfino.models.pyproject_toml import PluginConfig

ALL_PLUGINS_ALL_COMMANDS = {
    "fake_plugin_a": PluginConfig.empty(),
    "fake_plugin_b": PluginConfig.empty(),
    "fake-plugin-init-only": PluginConfig.empty(),
}


class FakeCommandFile(BaseModel):
    filename: str = "demo.py"
    command_name: str = "demo"
    content_template: str = "import click\n@click.command()\ndef {command_name}():\n    pass\n"

    @property
    def content(self) -> str:
        return self.content_template.format(**self.model_dump(exclude={"content_template"}))


@contextmanager
def demo_commands(
    folder_name: Path = DEFAULT_LOCAL_COMMAND_FOLDERS[0],
    fake_command_files: Iterable[FakeCommandFile] = (FakeCommandFile(),),
) -> Iterator[list[str]]:
    with tempfile.TemporaryDirectory() as tmpdir:
        root_dir = tmpdir / folder_name
        root_dir.mkdir(exist_ok=True)
        (root_dir / "__init__.py").touch()
        for fake_command_file in fake_command_files:
            (root_dir / fake_command_file.filename).write_text(fake_command_file.content)
        sys.path.append(tmpdir)
        try:
            yield [fake_command_file.command_name for fake_command_file in fake_command_files]
        finally:
            sys.path.pop()
