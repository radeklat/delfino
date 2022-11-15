import logging

import pytest

from delfino.click_utils.command import CommandRegistry


@pytest.fixture(scope="module")
def command_packages():
    return list(CommandRegistry._discover_command_packages())


@pytest.mark.usefixtures("install_fake_plugins")
class TestPlugin:
    @staticmethod
    def should_register_non_duplicated_plugin_commands(command_packages):
        registry = CommandRegistry(
            disabled_commands={"fake-plugin-a": set(["typecheck"])},
            command_packages=command_packages,  # don't load project packages
        )
        assert registry.visible_commands == ["format", "lint", "typecheck"]

    @staticmethod
    def should_raise_error_with_duplicated_plugin_commands(caplog, command_packages):
        caplog.set_level(logging.DEBUG)
        CommandRegistry(disabled_commands={}, command_packages=command_packages)
        log_msg = (
            "Using command 'typecheck' from plugin 'fake-plugin-b'. Previously registered "
            "by 'fake-plugin-a' plugin, which has lower priority."
        )
        assert log_msg in caplog.text
