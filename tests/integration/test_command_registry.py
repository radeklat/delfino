import logging
from pathlib import Path
from typing import Dict, Set

import pytest

from delfino.click_utils.command import CommandRegistry
from delfino.constants import DEFAULT_LOCAL_COMMANDS_DIRECTORY
from delfino.models.pyproject_toml import PluginConfig
from tests.integration.fixtures import ALL_PLUGINS_ALL_COMMANDS, demo_command


@pytest.fixture(scope="module")
def command_packages():
    return CommandRegistry._discover_command_packages(ALL_PLUGINS_ALL_COMMANDS)  # don't load project packages


@pytest.mark.usefixtures("install_fake_plugins")
class TestCommandRegistry:
    @staticmethod
    def should_deduplicate_plugin_commands(command_packages):
        registry = CommandRegistry(ALL_PLUGINS_ALL_COMMANDS, command_packages)
        assert {command.name for command in registry.visible_commands} == {"build", "format", "lint", "typecheck"}

    @staticmethod
    @pytest.mark.parametrize(
        "first_plugin_name, second_plugin_name",
        [
            pytest.param("fake-plugin-a", "fake-plugin-b", id="when A is first"),
            pytest.param("fake-plugin-b", "fake-plugin-a", id="when B is first"),
        ],
    )
    def should_load_plugins_in_specified_order(first_plugin_name: str, second_plugin_name: str):
        # GIVEN
        plugins_configs = {
            first_plugin_name: PluginConfig(enable_commands={"typecheck"}),
            second_plugin_name: PluginConfig(enable_commands={"typecheck"}),
        }

        # WHEN
        command_packages = CommandRegistry._discover_command_packages(plugins_configs)
        registry = CommandRegistry(plugins_configs, command_packages)

        # THEN
        assert registry.visible_commands
        command = next(iter(registry.visible_commands))
        assert command.name == "typecheck"
        assert command.package.plugin_name == second_plugin_name

    @staticmethod
    def should_log_when_duplicated_plugin_commands_are_ignored(caplog, command_packages):
        caplog.set_level(logging.DEBUG)
        CommandRegistry(ALL_PLUGINS_ALL_COMMANDS, command_packages)
        log_msg = (
            "Using command 'typecheck' from plugin 'fake-plugin-b'. Previously registered "
            "by 'fake-plugin-a' plugin, which has lower priority."
        )
        assert log_msg in caplog.text

    @staticmethod
    def should_warn_about_config_for_missing_plugin(caplog):
        # GIVEN
        caplog.set_level(logging.WARNING)

        # WHEN
        plugins_configs = {"not-a-plugin": PluginConfig.empty()}
        command_packages = CommandRegistry._discover_command_packages(plugins_configs)
        registry = CommandRegistry(plugins_configs, command_packages)

        # THEN
        assert "Plugin 'not-a-plugin' specified in config but no such plugin is installed." in caplog.text
        assert not registry.visible_commands
        assert not registry.hidden_commands

    @staticmethod
    def should_ignore_files_starting_with_an_underscore():
        model_path = Path("underscore_only")
        with demo_command(model_path, "_demo.py"):
            registry = CommandRegistry({}, local_commands_directory=model_path)
            assert not registry.visible_commands
            assert not registry.hidden_commands


@pytest.mark.usefixtures("install_fake_plugins")
class TestCommandRegistryPluginAndCommandSelection:
    @pytest.mark.parametrize(
        "plugins_configs, expected_visible_commands, expected_hidden_commands",
        [
            pytest.param({}, set(), set(), id="no plugins when none selected"),
            pytest.param(
                {"fake-plugin-a": PluginConfig(enable_commands={"lint"})},
                {"lint"},
                {"typecheck", "build"},
                id="only selected plugin and command",
            ),
            pytest.param(
                {
                    "fake-plugin-a": PluginConfig(enable_commands={"lint"}),
                    "fake-plugin-b": PluginConfig(enable_commands={"typecheck"}),
                },
                {"lint", "typecheck"},
                {"format", "build"},  # typecheck from fake-plugin-b should not appear
                id="only selected plugins and commands",
            ),
            pytest.param(
                {"fake-plugin-a": PluginConfig.empty()},
                {"lint", "typecheck", "build"},
                set(),
                id="all plugin commands when no enable nor disable specified",
            ),
            pytest.param(
                {"fake-plugin-a": PluginConfig(disable_commands={"lint"})},
                {"typecheck", "build"},
                {"lint"},
                id="all except disabled commands",
            ),
            pytest.param(
                {
                    "fake-plugin-a": PluginConfig(
                        enable_commands={"typecheck", "build", "lint"}, disable_commands={"lint"}
                    )
                },
                {"typecheck", "build"},
                {"lint"},
                id="all enabled without disabled commands",
            ),
        ],
    )
    def should_load(
        self,
        plugins_configs: Dict[str, PluginConfig],
        expected_visible_commands: Set[str],
        expected_hidden_commands: Set[str],
    ):
        # GIVEN
        command_packages = CommandRegistry._discover_command_packages(plugins_configs)

        # WHEN
        registry = CommandRegistry(plugins_configs, command_packages)

        # THEN
        assert {command.name for command in registry.visible_commands} == expected_visible_commands
        assert {command.name for command in registry.hidden_commands} == expected_hidden_commands

    @staticmethod
    def should_load_from_init_file():
        model_path = Path("init_only")
        with demo_command(model_path, "__init__.py") as command_name:
            registry = CommandRegistry({}, local_commands_directory=model_path)
            assert {command.name for command in registry.visible_commands} == {command_name}
            assert not registry.hidden_commands


class TestCommandRegistryLocalCommands:
    @staticmethod
    @pytest.mark.parametrize(
        "module_path, kwargs",
        [
            pytest.param(DEFAULT_LOCAL_COMMANDS_DIRECTORY, {}, id="the default folder"),
            pytest.param(Path("non_default"), {"local_commands_directory": Path("non_default")}, id="custom folder"),
        ],
    )
    def should_be_discovered_from(module_path, kwargs):
        with demo_command(module_path) as command_name:
            registry = CommandRegistry({}, **kwargs)
            assert command_name in {command.name for command in registry.visible_commands}
