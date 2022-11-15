import logging

import pytest

from delfino.click_utils.command import CommandRegistry
from tests.integration.fixtures import ALL_PLUGINS_ALL_COMMANDS


@pytest.fixture(scope="module")
def command_packages():
    return list(CommandRegistry._discover_command_packages(ALL_PLUGINS_ALL_COMMANDS))  # don't load project packages


# TODO(Radek): Test disabling plugins
# TODO(Radek): Test ordering plugins in config to prioritize commands from one plugin
# TODO(Radek): Test thoroughly enable and disable command lists
# TODO(Radek): Test fallback of disable_commands
# TODO(Radek): Test disabling/enabling local commands


@pytest.mark.usefixtures("install_fake_plugins")
class TestCommandRegistry:
    @staticmethod
    def should_deduplicate_plugin_commands(command_packages):
        registry = CommandRegistry(plugins_configs=ALL_PLUGINS_ALL_COMMANDS, command_packages=command_packages)
        assert registry.visible_commands == ["format", "lint", "typecheck"]

    @staticmethod
    def should_log_when_duplicated_plugin_commands_are_ignored(caplog, command_packages):
        caplog.set_level(logging.DEBUG)
        CommandRegistry(plugins_configs=ALL_PLUGINS_ALL_COMMANDS, command_packages=command_packages)
        log_msg = (
            "Using command 'typecheck' from plugin 'fake-plugin-b'. Previously registered "
            "by 'fake-plugin-a' plugin, which has lower priority."
        )
        assert log_msg in caplog.text
