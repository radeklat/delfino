import click
import pytest

from delfino.main import Commands


class TestExternalCommandsLoader:
    @staticmethod
    def should_load_plugins(install_fake_plugins):
        del install_fake_plugins
        loader = Commands.ExternalCommandsLoader()
        plugins = list(loader._load_plugins())
        assert len(list(plugins)) == 2
        assert "fake-plugin-a" in [plugin.name for plugin in plugins]

    @staticmethod
    def should_load_commands_without_collision(install_fake_plugins):
        del install_fake_plugins
        loader = Commands.ExternalCommandsLoader({"fake-plugin-b": set(["typecheck"])})
        commands = loader.load()
        assert len(commands.keys()) == 3
        assert commands["typecheck"]
        assert isinstance(commands["typecheck"], click.Command)

    @staticmethod
    def should_raise_error_with_collision(install_fake_plugins):
        del install_fake_plugins
        loader = Commands.ExternalCommandsLoader()
        with pytest.raises(RuntimeError):
            loader.load()
