from functools import update_wrapper
from typing import Any, Callable, TypeVar, cast
from warnings import warn

import click

_Func = TypeVar("_Func", bound=Callable[..., Any])


def filepaths_argument(func: _Func) -> _Func:
    warn(
        f"`@filepaths_argument` from `{__name__}` it deprecated. Use `decorators.files_folders_option` instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    @click.argument("filepaths", nargs=-1, type=click.Path(exists=True))
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        return ctx.invoke(func, *args, **kwargs)

    return update_wrapper(cast(_Func, new_func), func)
