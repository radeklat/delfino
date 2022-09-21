from delfino.plugin import discover_packages


class TestPlugin:
    @staticmethod
    def should_discover_packages(install_fake_plugins):
        del install_fake_plugins
        packages = list(discover_packages())
        assert len(packages) == 2
        plugin_names = [pak.plugin_name for pak in packages]
        assert "fake-plugin-a" in plugin_names
        assert "fake-plugin-b" in plugin_names

        fake_plugin_a_package = next(filter(lambda pak: pak.plugin_name == "fake-plugin-a", packages), None)
        assert "fake_plugin_a.commands" in fake_plugin_a_package.package.__package__
