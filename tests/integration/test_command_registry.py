import pytest

from delfino.main import _CommandRegistry
from delfino.plugin import discover_packages


class TestPlugin:
    @staticmethod
    def should_register_non_duplicated_plugin_commands(install_fake_plugins):
        del install_fake_plugins
        registry = _CommandRegistry(disabled_command={"fake-plugin-a": set(["typecheck"])})
        packages = list(discover_packages())
        for package in packages:
            registry.register_command_package(package)
        assert len(registry.as_dict()) == 3

    @staticmethod
    def should_raise_error_with_duplicated_plugin_commands(install_fake_plugins):
        del install_fake_plugins
        registry = _CommandRegistry(disabled_command={})
        packages = list(discover_packages())
        with pytest.raises(RuntimeError):
            for package in packages:
                registry.register_command_package(package)
