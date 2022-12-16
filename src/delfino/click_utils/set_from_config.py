from logging import getLogger
from typing import Any, Dict, Optional

import click
from click import BadParameter

from delfino.models import AppContext

_LOG = getLogger(__name__)


class SetOptionFromConfigCallback:
    """If config option exists in config and not set via command line, it will be used instead.

    Config option is looked up at ``tool.delfino.plugins.<PLUGIN>.<COMMAND NAME>.<COMMAND_ARGUMENT_NAME>``.
    """

    def __init__(self, command_argument_name: str, config_option_name: Optional[str] = None):
        self.config_option_name = config_option_name or command_argument_name
        self.command_argument_name = command_argument_name

    def _type_cast_value(self, ctx: click.Context, param: click.Parameter, value_from_config: Any) -> Any:
        try:
            return param.type_cast_value(ctx, value_from_config)
        except BadParameter as exc:
            exc.param_hint = f"the '{ctx.info_name}.{self.config_option_name}' config option in pyproject.toml file"
            raise

    def parameter_from_config_in_group(self, ctx: click.Context, command: click.Command) -> Dict[str, Any]:
        """Returns key-value pair to set in invoking another command.

        Similarly to ``__call__``, it takes the value from config if it exists. It also checks
        if the command has a ``click.Parameter`` of the matching name.

        This is useful for invoking commands indirectly, for example in a group command.
        """
        app_context = ctx.find_object(AppContext)

        if app_context is None:
            raise RuntimeError("AppContext was expected to be set but none found.")

        command_config = getattr(app_context.plugin_config, command.name or "", {})

        if isinstance(command_config, dict):
            value_from_config = command_config.get(self.config_option_name, None)
        else:
            value_from_config = getattr(command_config, self.config_option_name, None)

        if value_from_config:
            for command_param in command.params:
                if isinstance(command_param, click.Parameter) and command_param.name == self.command_argument_name:
                    return {self.command_argument_name: self._type_cast_value(ctx, command_param, value_from_config)}
            _LOG.warning(
                f"Command '{command.name}' has no parameter '{self.command_argument_name}'. Please update the "
                f"pyproject.toml file, option '{command.name}.{self.config_option_name}'."
            )
        return {}

    def __call__(self, ctx: click.Context, param: click.Parameter, value: Any) -> Any:
        """Load passed arguments from config if none given on command line."""
        # Command line options have higher priority. Return them instead of options from the config file.
        if value:
            return value

        # No command line options provided, try to load them from config
        app_context = ctx.find_object(AppContext)

        if app_context is None:
            raise RuntimeError("AppContext was expected to be set but none found.")

        command_name: str = ctx.command.name or ""
        value_from_config: str = getattr(app_context.plugin_config, command_name, {}).get(self.config_option_name, None)
        if value_from_config:
            return self._type_cast_value(ctx, param, value_from_config)

        return value
