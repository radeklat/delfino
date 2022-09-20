from setuptools import find_packages, setup

setup(
    name="fake_plugin_a",
    version="0.0.1",
    url="https://dummy.com",
    author="John Doe",
    author_email="john@cookpad.com",
    description="Dummy plugin",
    packages=find_packages(),
    entry_points={"delfino.commands": "NOT_USING_THIS = fake_plugin_a.commands"},
)
