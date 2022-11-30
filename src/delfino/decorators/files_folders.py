import click

files_folders_option = click.option(
    "-f",
    "--file",
    "--folder",
    "files_folders",
    multiple=True,
    nargs=1,
    type=click.Path(exists=True),
    help="A file or a folder to pass to the downstream tool instead of the default ones. "
    "Can be supplied multiple times.",
)
