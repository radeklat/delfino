from importlib.resources import Package

from pydantic import BaseModel


class CommandPackage(BaseModel):
    """Hold importlib.resources.Package that include commands and metadata for delfino.

    Attributes:
        package (Package): A package that include commands.
        required (bool): One ore more commands from this package is required.
        new_name (str): Set when ``package`` is a legacy name and ``new_name`` should be used instead.
        plugin_name (str): Name of the plugin.
    """

    package: Package  # A bit wired to have package attr as Command*Package* but didn't came up with good name
    required: bool = True
    new_name: str = ""
    plugin_name: str = ""

    class Config:
        arbitrary_types_allowed = True
