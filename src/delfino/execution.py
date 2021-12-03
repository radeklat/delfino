import os
import shlex
import subprocess
from enum import Enum
from typing import Any, Dict

import click

from delfino.utils import ArgsType


class OnError(Enum):
    PASS = "pass"
    """Same as ``check=False``. Use when you're handling the return code yourself."""

    EXIT = "exit"
    """Same as ``check=True`` + red print of stdout/stderr + ``raise click.exception.Exit()``.
    Use when running commands where non-zero return code indicates an error, not a failed check."""

    ABORT = "abort"
    """Same as ``check=True`` + print of stdout/stderr + ``raise click.Abort()``.
    Use when running commands where non-zero return code indicates a failed check, not an error."""


def _normalize_args(args: ArgsType, shell: bool) -> ArgsType:
    if shell:  # when `shell`, `args` must be a string
        if isinstance(args, list):
            return " ".join(map(str, args))
    elif isinstance(args, str):  # when not `shell`, `args` must be a `Sequence`
        return shlex.split(args)

    return args


def _patch_env(env_update_path: Dict[str, Any] = None, env_update: Dict[str, Any] = None) -> Dict[str, str]:
    modified_env = os.environ.copy()

    if env_update_path or env_update:
        if env_update_path is None:
            env_update_path = {}

        if env_update is None:
            env_update = {}

        for key, value in env_update_path.items():
            modified_env[key] = str(value) + (":" + modified_env[key] if key in modified_env else "")

        modified_env.update({key: str(value) for key, value in env_update.items()})

    return modified_env


def _called_process_error_to_click_exception(
    args: ArgsType, on_error: OnError, exc: subprocess.CalledProcessError
) -> Exception:
    if on_error == OnError.EXIT:
        click.secho(f"\nError ({exc.returncode}) when calling {args!r}:", fg="red")

        if exc.stdout:
            click.secho(exc.stdout.decode(), fg="red")
        if exc.stderr:
            click.secho(exc.stderr.decode(), fg="red")

        return click.exceptions.Exit(code=exc.returncode)

    if exc.stdout:
        print(exc.stdout.decode())
    if exc.stderr:
        print(exc.stderr.decode())

    return click.exceptions.Abort()


def run(
    args: ArgsType,
    *popenargs,
    on_error: OnError,
    env_update_path: Dict[str, Any] = None,
    env_update: Dict[str, Any] = None,
    **kwargs,
) -> subprocess.CompletedProcess:
    """Modified version of ``subprocess.run``.

    Args:
        args: Program to run with all it's arguments. Passing a sequence is recommended. An
            attempt to parse a string (not bytes) will be made but may lead to an unintended
            split.
        *popenargs: Additional positional arguments passed directly to ``subprocess.run``.
        on_error: Similar to ``Popen(check)`` but differentiating between ``click.exceptions.Exit``
            and ``click.Abort``.
        env_update_path: A dict of path-like environment variables to update. If this variable already
            exists, the value will be pre-pended with a ":".
        env_update: Similar to ``env_update_path`` but any existing variables are replaced.
        **kwargs: Additional keyword arguments passed directly to ``subprocess.run``.
    """
    args = _normalize_args(args, kwargs.get("shell", False))
    kwargs["env"] = _patch_env(env_update_path, env_update)

    try:
        return subprocess.run(args, *popenargs, check=on_error != OnError.PASS, **kwargs)
    except subprocess.CalledProcessError as exc:
        raise _called_process_error_to_click_exception(args, on_error, exc) from exc
