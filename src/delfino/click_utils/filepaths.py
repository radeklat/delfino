import click

filepaths_argument = click.argument(
    "filepaths",
    nargs=-1,
    type=click.Path(exists=True),
)
