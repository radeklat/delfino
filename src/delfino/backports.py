import shlex
from typing import Iterable


def shlex_join(split_command: Iterable[str]) -> str:
    """Return a shell-escaped string from *split_command*.

    Backport of ``shlex.join`` for Python 3.7
    """
    return " ".join(shlex.quote(arg) for arg in split_command)
