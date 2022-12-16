import click

from delfino.click_utils.set_from_config import SetOptionFromConfigCallback

_ARGUMENT_NAME: str = "files_folders"
FILES_FOLDERS_OPTION_CALLBACK = SetOptionFromConfigCallback(_ARGUMENT_NAME)

files_folders_option = click.option(
    "-f",
    "--file",
    "--folder",
    _ARGUMENT_NAME,
    multiple=True,
    nargs=1,
    type=click.Path(exists=True),
    help="A file or a folder to pass to the downstream tool instead of the default ones. "
    "Can be supplied multiple times.",
    callback=FILES_FOLDERS_OPTION_CALLBACK,
)
