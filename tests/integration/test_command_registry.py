import logging
from pathlib import Path
from typing import Dict, Set

import pytest

from delfino.click_utils.command import CommandRegistry
from delfino.constants import DEFAULT_LOCAL_COMMAND_FOLDERS
from delfino.models.pyproject_toml import PluginConfig
from tests.integration.fixtures import ALL_PLUGINS_ALL_COMMANDS, FakeCommandFile, demo_commands


@pytest.fixture(scope="module")
def command_packages():
    return CommandRegistry._discover_command_packages(ALL_PLUGINS_ALL_COMMANDS)  # don't load project packages


class TestCommandRegistry:
    @staticmethod
    @pytest.mark.usefixtures("install_fake_plugins")
    def should_deduplicate_plugin_commands(command_packages):
        registry = CommandRegistry(ALL_PLUGINS_ALL_COMMANDS, command_packages)
        assert {command.name for command in registry.visible_commands} == {"build", "format", "lint", "typecheck"}

    @staticmethod
    @pytest.mark.usefixtures("install_fake_plugins")
    @pytest.mark.parametrize(
        "first_plugin_name, second_plugin_name",
        [
            pytest.param("fake_plugin_a", "fake_plugin_b", id="when A is first"),
            pytest.param("fake_plugin_b", "fake_plugin_a", id="when B is first"),
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
    @pytest.mark.usefixtures("install_fake_plugins")
    def should_log_when_duplicated_plugin_commands_are_ignored(caplog, command_packages):
        caplog.set_level(logging.DEBUG)
        CommandRegistry(ALL_PLUGINS_ALL_COMMANDS, command_packages)
        log_msg = (
            "Using command 'typecheck' from plugin 'fake_plugin_b'. Previously registered "
            "by 'fake_plugin_a' plugin, which has lower priority."
        )
        assert log_msg in caplog.text

    @staticmethod
    @pytest.mark.usefixtures("install_fake_plugins")
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
    @pytest.mark.usefixtures("install_fake_plugins")
    @pytest.mark.parametrize(
        "group_name, registry_group_with_commands, empty_registry_group",
        [
            pytest.param("disable", "visible_commands", "hidden_commands", id="that are disabled"),
            pytest.param("enable", "hidden_commands", "visible_commands", id="that are enabled"),
        ],
    )
    def should_warn_about_missing_commands(caplog, group_name: str, registry_group_with_commands, empty_registry_group):
        # GIVEN
        plugin_name = "fake_plugin_a"
        command_name = "missing-command"
        caplog.set_level(logging.WARNING)

        # WHEN
        plugin_config = PluginConfig.empty()
        setattr(plugin_config, f"{group_name}_commands", {command_name})
        plugins_configs = {plugin_name: plugin_config}
        command_packages = CommandRegistry._discover_command_packages(plugins_configs)
        registry = CommandRegistry(plugins_configs, command_packages)

        # THEN
        warning_message = (
            f"{group_name.capitalize()}d command '{command_name}' from the '{plugin_name}' "
            "plugin in config does not exist. This can be a typo in the command name or "
            "the command has been removed/renamed. Please update the 'pyproject.toml' file."
        )
        assert warning_message in caplog.text
        assert not getattr(registry, empty_registry_group)
        assert {command.name for command in getattr(registry, registry_group_with_commands)} == {
            "typecheck",
            "build",
            "lint",
        }

    @staticmethod
    def should_ignore_files_starting_with_an_underscore():
        model_path = Path("underscore_only")
        with demo_commands(model_path, [FakeCommandFile(filename="_demo.py")]):
            registry = CommandRegistry({}, local_command_folders=[model_path])
            assert not registry.visible_commands
            assert not registry.hidden_commands

    @staticmethod
    def should_not_load_commands_that_come_from_import_statements_and_start_with_an_underscore():
        model_path = Path("imported_command")
        fake_command_files = [
            FakeCommandFile(
                command_name="_ignored",
                filename="inspected.py",
                content_template="from ._not_inspected import demo as _demo\n",
            ),
            FakeCommandFile(filename="_not_inspected.py"),
        ]
        with demo_commands(model_path, fake_command_files):
            registry = CommandRegistry({}, local_command_folders=[model_path])
            assert not registry.visible_commands
            assert not registry.hidden_commands

    @staticmethod
    def should_not_load_sub_commands_of_a_group():
        model_path = Path("group_command")
        fake_command_files = [
            FakeCommandFile(
                content_template="import click\n"
                "@click.group()\ndef visible_group():\n    pass\n"
                "@visible_group.group()\ndef hidden_group():\n    pass\n"
                "@hidden_group.command()\ndef hidden_sub_command():\n    pass\n",
            ),
        ]
        with demo_commands(model_path, fake_command_files):
            registry = CommandRegistry({}, local_command_folders=[model_path])
            assert {command.name for command in registry.visible_commands} == {"visible-group"}
            assert not registry.hidden_commands


@pytest.mark.usefixtures("install_fake_plugins")
class TestCommandRegistryPluginAndCommandSelection:
    @pytest.mark.parametrize(
        "plugins_configs, expected_visible_commands, expected_hidden_commands",
        [
            pytest.param({}, set(), set(), id="no plugins when none selected"),
            pytest.param(
                {"fake_plugin_a": PluginConfig(enable_commands={"lint"})},
                {"lint"},
                {"typecheck", "build"},
                id="only selected plugin and command",
            ),
            pytest.param(
                {
                    "fake_plugin_a": PluginConfig(enable_commands={"lint"}),
                    "fake_plugin_b": PluginConfig(enable_commands={"typecheck"}),
                },
                {"lint", "typecheck"},
                {"format", "build"},  # typecheck from fake_plugin_b should not appear
                id="only selected plugins and commands",
            ),
            pytest.param(
                {"fake_plugin_a": PluginConfig.empty()},
                {"lint", "typecheck", "build"},
                set(),
                id="all plugin commands when no enable nor disable specified",
            ),
            pytest.param(
                {"fake_plugin_a": PluginConfig(disable_commands={"lint"})},
                {"typecheck", "build"},
                {"lint"},
                id="all except disabled commands",
            ),
            pytest.param(
                {
                    "fake_plugin_a": PluginConfig(
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
        with demo_commands(model_path, [FakeCommandFile(filename="__init__.py")]) as command_names:
            registry = CommandRegistry({}, local_command_folders=[model_path])
            assert {command.name for command in registry.visible_commands} == {command_names[0]}
            assert not registry.hidden_commands


class TestCommandRegistryLocalCommands:
    @staticmethod
    @pytest.mark.parametrize(
        "module_path, kwargs",
        [
            pytest.param(DEFAULT_LOCAL_COMMAND_FOLDERS[0], {}, id="the default folders"),
            pytest.param(Path("non_default"), {"local_command_folders": [Path("non_default")]}, id="custom folder"),
        ],
    )
    def should_be_discovered_from(module_path, kwargs):
        with demo_commands(module_path) as command_names:
            registry = CommandRegistry({}, **kwargs)
            assert set(command_names) <= {command.name for command in registry.visible_commands}
