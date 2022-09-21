"""Functions to load packages includes commands from plugins."""
import sys
from typing import Iterator

from delfino.models.command_package import CommandPackage

if sys.version_info < (3, 10):
    from importlib_metadata import distributions
else:
    from importlib.metadata import distributions


def discover_packages(plugin_group_name: str = "delfino.commands") -> Iterator[CommandPackage]:
    """Discover packages from plugin. It is using package metadata as plugin discovering solution.

    Check the following URL about the plugin discovering solutions including the one uses package metadata.
    https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/

    Args:
        plugin_group_name (str): Used for a key to filter plugin for Delfino. Defaults to "delfino.commands".

    Yields:
        Iterator[CommandPackage]: Iterator of models.CommandPackage.
    """
    for distribution in distributions():
        for entry_point in distribution.entry_points.select(group=plugin_group_name):
            if not entry_point:
                continue
            yield CommandPackage(package=entry_point.load(), plugin_name=distribution.metadata["Name"])
