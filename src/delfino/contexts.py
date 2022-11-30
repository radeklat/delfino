from importlib import import_module
from warnings import warn

_deprecations = {"AppContext": "delfino.models", "pass_app_context": "delfino.decorators"}


def __getattr__(name):
    if name in _deprecations:
        new_module = _deprecations[name]
        warn(
            f"Import of `{name}` from `{__name__}` is deprecated. Use `{new_module}` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(import_module(new_module), name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
