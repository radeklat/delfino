import click
import toml

from toolbox.contexts import AppContext, pass_app_context


@click.command("init")
@pass_app_context
def run_init(app_context: AppContext):
    """Initializes toolbox for this project."""
    if not app_context.py_project_toml.tool.toolbox:
        if not click.confirm("'toolbox' section not found in 'pyproject.toml'. Create it?", default=True):
            raise click.Abort()

        with open(app_context.py_project_toml.file_path, "w", encoding="utf-8") as file:
            toml.dump({"tool": {"toolbox": {}}}, file)
