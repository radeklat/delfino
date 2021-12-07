from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Union

import click

from delfino.constants import ENTRY_POINT
from delfino.validation import assert_pip_package_installed

try:
    import shellingham
except ImportError:
    pass


class CompletionAlreadyInstalled(Exception):
    pass


@dataclass
class Completion:
    shell: str
    completion: str
    install: Callable[[str], Path]

    @property
    def formatted_completion(self) -> str:
        complete_var = f"_{ENTRY_POINT.replace('-', '_').upper()}_COMPLETE"
        return self.completion.format(entry_point=ENTRY_POINT, complete_var=complete_var).strip()


_COMPLETION_BASH = """
_complete_{entry_point}() {{
    [ -n "$(which {entry_point})" ] && \\
        eval "$({complete_var}=bash_source {entry_point})";
}}
complete -F _complete_{entry_point} -o default invoke {entry_point}
"""


def _install_completion_bash(formatted_completion: str) -> Path:
    rc_path = Path.home() / ".bashrc"
    rc_path.parent.mkdir(parents=True, exist_ok=True)
    rc_content = rc_path.read_text(encoding="utf-8") if rc_path.is_file() else ""
    if formatted_completion in rc_content:
        raise CompletionAlreadyInstalled()

    rc_path.write_text(f"{rc_content}\n{formatted_completion}", encoding="utf-8")

    return rc_path


_COMPLETIONS: Dict[str, Completion] = {
    "bash": Completion(shell="bash", completion=_COMPLETION_BASH, install=_install_completion_bash),
}


def _get_completion_for_current_shell() -> Completion:
    assert_pip_package_installed("shellingham")

    shell: str = shellingham.detect_shell()[0]
    try:
        return _COMPLETIONS[shell]
    except KeyError as exc:
        supported_shells = ", ".join(_.capitalize() for _ in _COMPLETIONS)
        click.secho(f"{shell.capitalize()} is not supported. Supported shells are: {supported_shells}", fg="red")
        raise click.Abort() from exc


def _show_completion_for_current_shell(ctx: click.Context, param: Union[click.Option, click.Parameter], value: bool):
    del param
    if not value or ctx.resilient_parsing:
        return
    click.secho(_get_completion_for_current_shell().formatted_completion)
    raise click.exceptions.Exit(0)


show_completion_option = click.option(
    "--show-completion",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=_show_completion_for_current_shell,
    help="Show completion for the current shell, to copy it or customize the installation.",
)


def _install_completion_for_current_shell(ctx: click.Context, param: Union[click.Option, click.Parameter], value: bool):
    del param
    if not value or ctx.resilient_parsing:
        return
    completion = _get_completion_for_current_shell()
    try:
        path = completion.install(completion.formatted_completion)
        click.secho(f"✔ {completion.shell.capitalize()} completion installed in '{path}'.", fg="green")
        click.secho("⚠ Completion will take effect once you restart the terminal.", fg="yellow")
    except CompletionAlreadyInstalled:
        click.secho(
            f"✔ {completion.shell.capitalize()} completion has been previously installed. Not installing again.",
            fg="green",
        )

    raise click.exceptions.Exit(0)


install_completion_option = click.option(
    "--install-completion",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=_install_completion_for_current_shell,
    help="Install completion for the current shell.",
)
