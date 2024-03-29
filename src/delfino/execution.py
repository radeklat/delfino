import os
import shlex
import subprocess
from enum import Enum
from logging import getLogger
from typing import Any, Callable, Dict, Final, Optional, Tuple

import click

from delfino.utils import ArgsType

_LOG = getLogger(__name__)


class OnError(Enum):
    PASS: Final[str] = "pass"
    """Same as ``check=False``. Use when you're handling the return code yourself."""

    EXIT: Final[str] = "exit"
    """Same as ``check=True`` + red print of stdout/stderr + ``raise click.exception.Exit()``.
    Use when running commands where non-zero return code indicates an error, not a failed check."""

    ABORT: Final[str] = "abort"
    """Same as ``check=True`` + print of stdout/stderr + ``raise click.Abort()``.
    Use when running commands where non-zero return code indicates a failed check, not an error."""


def _normalize_args(args: ArgsType, shell: bool) -> Tuple[ArgsType, str]:
    if shell:  # when `shell`, `args` must be a string
        if isinstance(args, str):
            return args, args

        if isinstance(args, bytes):
            args_decoded = args.decode()
            return args_decoded, args_decoded

        args_str = shlex.join(map(str, args))
        return args_str, args_str

    # when not `shell`, `args` must be a `Sequence`
    if isinstance(args, str):
        return shlex.split(args), args

    if isinstance(args, bytes):
        args_decoded = args.decode()
        return shlex.split(args_decoded), args_decoded

    args_list = [str(arg) for arg in args]
    return args_list, shlex.join(args_list)


def _patch_env(
    env_update_path: Optional[Dict[str, Any]] = None, env_update: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
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
    env_update_path: Optional[Dict[str, Any]] = None,
    env_update: Optional[Dict[str, Any]] = None,
    running_hook: Optional[Callable[[], None]] = None,
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
        running_hook: If provided, the process will be polled for return code and this function will
            be called every time the process has not finished yet. The function should contain a
            suitable wait interval to not check the result too frequently.
        **kwargs: Additional keyword arguments passed directly to ``subprocess.run``.
    """
    args, printable_args = _normalize_args(args, kwargs.get("shell", False))
    kwargs["env"] = _patch_env(env_update_path, env_update)

    _LOG.debug(printable_args)

    try:
        with subprocess.Popen(args, *popenargs, **kwargs) as process:
            if running_hook is not None:
                while process.poll() is None:
                    running_hook()
            try:
                stdout, stderr = process.communicate(timeout=kwargs.get("timeout", None))
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise
            except Exception:  # Including KeyboardInterrupt, communicate handled that.
                process.kill()
                # We don't call process.wait() as .__exit__ does that for us.
                raise
            retcode = process.poll()
            if on_error != OnError.PASS and retcode:
                raise subprocess.CalledProcessError(retcode, process.args, output=stdout, stderr=stderr)
        return subprocess.CompletedProcess(process.args, retcode or 0, stdout, stderr)
    except subprocess.CalledProcessError as exc:
        raise _called_process_error_to_click_exception(args, on_error, exc) from exc
