from types import ModuleType

import pytest

from delfino.click_utils.command import CommandRegistry


@pytest.mark.usefixtures("install_fake_plugins")
class TestPlugin:
    @staticmethod
    def should_discover_packages():
        command_packages = list(CommandRegistry._discover_command_packages())
        assert len(command_packages) == 2
        plugin_names = {command_package.plugin_name for command_package in command_packages}
        assert "fake-plugin-a" in plugin_names
        assert "fake-plugin-b" in plugin_names

        fake_plugin_a_package = next(
            filter(lambda command_package: command_package.plugin_name == "fake-plugin-a", command_packages), None
        )
        assert fake_plugin_a_package
        assert isinstance(fake_plugin_a_package.package, ModuleType)
        assert isinstance(fake_plugin_a_package.package.__package__, str)
        assert "fake_plugin_a.commands" in fake_plugin_a_package.package.__package__
