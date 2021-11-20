"""General-purpose utilities for this project's pyinvoke tasks."""
import os
import re
import shutil
from pathlib import Path

from click import secho
from invoke import Context

from toolbox.constants import Project


def ensure_reports_dir(project: Project) -> None:
    """Ensures that the reports directory exists."""
    project.reports_directory.mkdir(parents=True, exist_ok=True)


def read_contents(fpath: Path, strip_newline=True) -> str:
    """Read plain text file contents as string."""
    with open(fpath, encoding="utf-8") as f_in:
        contents = "".join(f_in.readlines())
        if strip_newline:
            contents = contents.rstrip("\n")
        return contents


def format_messages(messages: str, success_pattern: str = "^$"):
    if re.match(success_pattern, messages, re.DOTALL):
        secho("✔ No issues found.", fg="green")
    else:
        print(messages)


def ensure_pre_commit(ctx: Context):
    ctx.run("pre-commit install", pty=True, hide="both")


_HEADER_LEVEL_CHARACTERS = {1: "#", 2: "=", 3: "-"}


def print_header(text: str, level: int = 1, icon: str = ""):
    if icon:
        icon += " "

    padding_character = _HEADER_LEVEL_CHARACTERS[level]
    if os.getenv("CIRCLECI", ""):
        padding_length = 80
    else:
        padding_length = max(shutil.get_terminal_size((80, 20)).columns - (len(icon) * 2), 0)

    padding = f"\n{{:{padding_character}^{padding_length}}}\n"
    if level == 1:
        text = text.upper()
    print(padding.format(f" {icon}{text} {icon}"))
