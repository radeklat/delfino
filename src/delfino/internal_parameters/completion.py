import functools
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Union

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
        return self.completion.format(entry_point=ENTRY_POINT, entry_point_upper=ENTRY_POINT.upper()).strip()


_COMPLETION_BASH = """
_complete_{entry_point}() {{
    [ -n "$(which {entry_point})" ] && \\
        eval "$(_{entry_point_upper}_COMPLETE=bash_source {entry_point})";
}}
complete -F _complete_{entry_point} -o default invoke {entry_point}
"""

_COMPLETION_ZSH = """
_complete_{entry_point}() {{
    which {entry_point} >/dev/null && \\
        eval $(_{entry_point_upper}_COMPLETE=zsh_source {entry_point})
}}
compctl -K _complete_{entry_point} + -f invoke {entry_point}
"""


def handle_assertion_error(func):
    @functools.wraps(func)
    def inner(ctx: click.Context, param: Union[click.Option, click.Parameter], value: bool):
        try:
            return func(ctx, param, value)
        except AssertionError as exc:
            click.secho(str(exc), fg="red", err=True)
            raise click.exceptions.Exit(1) from exc

    return inner


def _install_completion(
    formatted_completion: str, *, completion_path: Path, completion_init_lines: List[str], rc_path: Path
) -> Path:
    rc_path.parent.mkdir(parents=True, exist_ok=True)
    rc_content = rc_path.read_text(encoding="utf-8") if rc_path.is_file() else ""

    content_added = False
    for line in completion_init_lines:
        if line not in rc_content:  # pragma: nocover
            rc_content += f"\n{line}"
            content_added = True

    if not content_added:
        raise CompletionAlreadyInstalled()

    rc_content += "\n"
    rc_path.write_text(rc_content)

    # Install completion
    completion_path.parent.mkdir(parents=True, exist_ok=True)
    completion_path.write_text(formatted_completion)
    return completion_path


def _install_completion_bash(formatted_completion: str) -> Path:
    completion_path = Path.home() / f".bash_completions/{ENTRY_POINT}.sh"
    return _install_completion(
        formatted_completion,
        completion_path=completion_path,
        completion_init_lines=[f"source {completion_path}"],
        rc_path=Path.home() / ".bashrc",
    )


def _install_completion_zsh(formatted_completion: str) -> Path:
    return _install_completion(
        formatted_completion,
        completion_path=Path.home() / f".zfunc/_{ENTRY_POINT}",
        completion_init_lines=[
            "autoload -Uz compinit",
            "compinit",
            "zstyle ':completion:*' menu select",
            "fpath+=~/.zfunc",
        ],
        rc_path=Path.home() / ".zshrc",
    )


_COMPLETIONS: Dict[str, Completion] = {
    "bash": Completion(shell="bash", completion=_COMPLETION_BASH, install=_install_completion_bash),
    "zsh": Completion(shell="zsh", completion=_COMPLETION_ZSH, install=_install_completion_zsh),
}


def _get_completion_for_current_shell(param: Union[click.Option, click.Parameter]) -> Completion:
    assert_pip_package_installed("shellingham", required_by=f"{param.param_type_name} --{param.name}")

    shell: str = shellingham.detect_shell()[0]
    try:
        return _COMPLETIONS[shell]
    except KeyError as exc:
        supported_shells = ", ".join(_.capitalize() for _ in _COMPLETIONS)
        click.secho(f"{shell.capitalize()} is not supported. Supported shells are: {supported_shells}", fg="red")
        raise click.Abort() from exc


@handle_assertion_error
def _show_completion_for_current_shell(ctx: click.Context, param: Union[click.Option, click.Parameter], value: bool):
    if not value or ctx.resilient_parsing:
        return
    click.secho(_get_completion_for_current_shell(param).formatted_completion)
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
    if not value or ctx.resilient_parsing:
        return
    completion = _get_completion_for_current_shell(param)
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
