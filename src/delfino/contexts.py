import functools
from pathlib import Path
from typing import Any, Callable, Type, TypeVar, cast

from click import get_current_context
from pydantic import BaseModel

from delfino.constants import PackageManager
from delfino.models.pyproject_toml import PluginConfig, PyprojectToml


class AppContext(BaseModel):
    project_root: Path
    pyproject_toml: PyprojectToml
    package_manager: PackageManager
    plugin_config: PluginConfig

    class Config:
        arbitrary_types_allowed = True


_Func = TypeVar("_Func", bound=Callable[..., Any])


def pass_app_context(plugin_config_type: Type[PluginConfig] = PluginConfig) -> Callable[[_Func], _Func]:
    """Similar to ``click.make_pass_decorator``, with optional parsing of plugin specific config.

    This decorator passes into the command an app context ``AppContext``. In this context,
    the ``plugin_config`` attribute holds a config specific to the plugin where the called
    command originates. Any unknown fields will be kept. If you want to parse and validate
    this config, pass a subclass of ``PluginConfig`` as the ``plugin_config_type`` argument
    of this decorator. ``plugin_config`` will be then replaced with this instance, provided
    it is valid.

    Args:
        plugin_config_type: A subclass of ``PluginConfig``.
    """

    def decorator(func: _Func) -> _Func:
        def new_func(*args, **kwargs):
            ctx = get_current_context()
            obj = ctx.find_object(AppContext)
            if obj is None:
                raise RuntimeError(
                    f"Managed to invoke callback without a context object of type {AppContext.__name__!r} existing."
                )
            obj.plugin_config = plugin_config_type.from_orm(obj.plugin_config)
            return ctx.invoke(func, obj, *args, **kwargs)

        return functools.update_wrapper(cast(_Func, new_func), func)

    return decorator
