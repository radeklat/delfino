from setuptools import find_packages, setup

setup(
    name="fake_plugin_a",
    version="0.0.1",
    url="https://example.com",
    author="Test",
    author_email="test@example.com",
    description="Dummy plugin",
    packages=find_packages(),
    entry_points={"delfino.plugin": "fake_plugin_a = fake_plugin_a.commands"},
)
