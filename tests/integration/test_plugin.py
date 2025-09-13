from types import ModuleType

import pytest

from delfino.click_utils.command import CommandRegistry
from tests.integration.fixtures import ALL_PLUGINS_ALL_COMMANDS


@pytest.mark.usefixtures("install_fake_plugins")
class TestPlugin:
    @staticmethod
    def test_should_discover_packages():
        command_packages = CommandRegistry._discover_command_packages(ALL_PLUGINS_ALL_COMMANDS)
        plugin_names = {command_package.plugin_name for command_package in command_packages}
        assert plugin_names == {"fake_plugin_a", "fake_plugin_b"}

        fake_plugin_a_package = next(
            filter(
                lambda command_package: command_package.plugin_name == "fake_plugin_a",
                command_packages,
            ),
            None,
        )
        assert fake_plugin_a_package
        assert isinstance(fake_plugin_a_package.package, ModuleType)
        assert isinstance(fake_plugin_a_package.package.__package__, str)
        assert "fake_plugin_a.commands" in fake_plugin_a_package.package.__package__
