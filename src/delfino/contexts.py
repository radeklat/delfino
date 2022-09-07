import subprocess
from contextlib import contextmanager
from email import contentmanager
from pathlib import Path
from typing import Any, Dict, Optional

from click import make_pass_decorator
from pydantic import BaseModel

from delfino.constants import PackageManager
from delfino.execution import OnError, run
from delfino.models.pyproject_toml import PyprojectToml
from delfino.utils import ArgsType


class AppContext(BaseModel):
    project_root: Path
    pyproject_toml: PyprojectToml
    package_manager: PackageManager
    _env_update_path: Optional[Dict[str, Any]] = None
    _env_update: Optional[Dict[str, Dict]] = None

    class Config:
        arbitrary_types_allowed = True

    @contextmanager
    def set_env(self, env_update_path: Optional[Dict[str, Any]] = None, env_update: Optional[Dict[str, Any]] = None):
        """Set environment variable for the context.

        Args:
            env_update_path: Same as ``delfino.execution.run``.
            env_update: Same as ``delfino.execution.run``.
        """
        self._env_update_path = env_update_path
        self._env_update = env_update
        try:
            yield self
        finally:
            self._env_update_path = None
            self._env_update = None

    @property
    def env_update_path(self) -> Dict[str, Any]:
        return self._env_update_path or {}

    @property
    def env_update(self) -> Dict[str, Any]:
        return self._env_update or {}

    def run(
        self,
        args: ArgsType,
        *popenargs,
        on_error: OnError,
        env_update_path: Dict[str, Any] = None,
        env_update: Dict[str, Any] = None,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        """Context enabled version of ``delfino.execution.run``.

        Args:
            args: Same as ``delfino.execution.run``.
            *popenargs: Same as ``delfino.execution.run``.
            on_error: Same as ``delfino.execution.run``.
                and ``click.Abort``.
            env_update_path: Same as ``delfino.execution.run`` but ``self.env_update_path``
                will be merged if not None.
            env_update: Same as ``delfino.execution.run`` but ``self.env_update`` will be
                merged if not None.
            **kwargs: Same as ``delfino.execution.run``.
        """
        _env_update_path = self._env_update_path | (env_update_path or {})
        _env_update = self._env_update | (env_update or {})

        return run(
            args, *popenargs, on_error=on_error, env_update_path=_env_update_path, env_update=_env_update, **kwargs
        )


pass_app_context = make_pass_decorator(AppContext)
