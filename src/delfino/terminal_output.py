import os
import shutil

import click

from delfino.constants import ENTRY_POINT, PackageManager
from delfino.models.app_context import AppContext


def print_no_issues_found():
    click.secho("✔ No issues found.", fg="green")


_HEADER_LEVEL_CHARACTERS = {1: "#", 2: "=", 3: "-"}


def print_header(text: str, level: int = 1, icon: str = ""):
    icon_pad = " " if icon else ""

    padding_character = _HEADER_LEVEL_CHARACTERS[level]
    if os.getenv("CIRCLECI", ""):
        padding_length = 80
    else:
        padding_length = max(shutil.get_terminal_size((80, 20)).columns - (len(icon) * 2), 0)

    padding = f"\n{{:{padding_character}^{padding_length}}}\n"
    if level == 1:
        text = text.upper()
    print(padding.format(f" {icon}{icon_pad}{text} {icon[::-1 if len(icon) > 1 else 1]}{icon_pad}"))


def run_command_example(command: click.Command, app_context: AppContext) -> str:
    prefix = ""
    if app_context.package_manager != PackageManager.UNKNOWN:
        prefix = f"{app_context.package_manager.value} run "
    return f"{prefix}{ENTRY_POINT} {command.name}"
