# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).
Types of changes are:

- **Breaking changes** for breaking changes.
- **Features** for new features or changes in existing functionality.
- **Fixes** for any bug fixes.
- **Deprecated** for soon-to-be removed features.

## [Unreleased]

## [5.0.0] - 2025-09-13

### Breaking changes

- Raised minimum supported version of Click from 8.0 to 8.2.0 due to deprecation of `click.MultiCommand`. This version also drops support for Python 3.7-3.9.
- Dropped support for Python 3.9.

### Features

- Add support for `uv` (https://uv.pypa.io/) as a package manager.

## [4.0.0] - 2025-08-09

### Breaking changes

- Drop support for Python 3.8. Type annotations now use Python 3.9+ style generics (list, dict, tuple) and PEP 604 unions.

### Features

- Detect `uv` as a package manager when `tool.uv` is present in `pyproject.toml`, when `uv.lock` exists, or via `build-system.requires`.
- Upgrade `delfino-core` from 7.x to 9.x. Most linting and formatting are now handled by `ruff` instead of previously used tools like `black` and `isort`.

### Fixes

- Fixed several typing errors previously undetected by the tooling.
- Upgrade of all dependencies.

## [3.1.2] - 2024-06-20

### Fixes

- Hide sub-commands based on function name, not the command name.

## [3.1.1] - 2024-01-23

### Fixes

- Wrong order of inheritance for `pydantic.BaseModel` and `Generic`, generating a warning.

## [3.1.0] - 2023-10-24

### Features

- Add `running_hook` to `execution.run` to allow showing progress of a slow running tool.

## [3.0.2] - 2023-10-20

### Fixes

- Hide sub-commands from top level help.

## [3.0.1] - 2023-10-12

### Fixes

- Dependencies update
- Removal of Python 3.7 compatibility code

## [3.0.0] - 2023-09-14

### Breaking changes

- Upgrade `pydantic` dependency from `1.x` to `2.x`.

## [2.0.0] - 2023-06-25

### Breaking changes

- Drops Python 3.7 support.
- Removes deprecated config option `tool.delfino.local_commands_directory`. See [1.3.0](#130---2023-05-13) for more details.

### Fixes

- Adds `typing.Final` type annotation and use of assignment operator where possible.

## [1.3.0] - 2023-05-13

### Deprecated

- Config option `tool.delfino.local_commands_directory` is now `tool.delfino.local_command_folders`. It is a list of folders to search for local commands (instead of a single folder). The default value is `["commands"]`. `delfino.models.pyproject_toml.Delfino.local_commands_directory` falls back to the first folder in `local_command_folder` and will be removed in the next major version.

## [1.2.0] - 2023-05-06

### Features

- Added support for config file named `.delfinorc`.

## [1.1.1] - 2023-05-06

### Fixes

- Dependencies updates.
- Fix typing issues. `command_groups` in settings are now validated (`tool.delfino` and `tool.delfino.plugins.<PLUGIN>`).

## [1.1.0] - 2022-12-29

### Features

- Warn about enabled or disabled commands that don't exist. This can be either due to a typo or because command has been removed/renamed.

## [1.0.0] - 2022-12-21

### Breaking changes

The following deprecations were removed:
- `contexts` module
- `delfino.click_utils.filepaths.filepaths_argument` decorator

## [0.30.0] - 2022-12-16

### Breaking changes

- Previously deprecated `delfino.click_utils.SetOptionFromConfigCallback.set_parameter_from_config_in_group` has been removed.

## [0.29.0] - 2022-12-16

### Features

- `run` logs executed commands in `DEBUG` log level.

### Deprecated

- `delfino.click_utils.SetOptionFromConfigCallback.set_parameter_from_config_in_group` in favours of `delfino.click_utils.SetOptionFromConfigCallback.parameter_from_config_in_group`.

## [0.28.1] - 2022-12-16

### Fixes

- `click_utils.SetOptionFromConfigCallback.set_parameter_from_config_in_group` working only for `click.Argument` and not `click.Option`.

## [0.28.0] - 2022-12-16

### Features

- `click_utils.SetOptionFromConfigCallback` that if used as a callback to `click.Parameter` sub-classes will get a value for the parameter from config if not provided on the command line.
- `decorators.files_folders` can be specified in config.

## [0.27.0] - 2022-12-15

### Features

- Add `decorators.pass_args.set_passed_args_from_config_in_group` to allow passing the `pass_args` value from config to command executed indirectly. 

### Fixes

- Dropping keys on plugin config re-parsing into more specific model. 

## [0.26.1] - 2022-12-12

### Fixes

- Suppress warning about missing plugin for local commands.

## [0.26.0] - 2022-12-07

### Features

- Ignore commands where the object name start with and underscore. This is to prevent reused commands being considered as originating from the imported location. For example, if you import `from plugin.commands import some_command as _some_command`, then `_some_command` will not be visible in Delfino. However, with `from plugin.commands import some_command`, `some_command` would be considered as being defined in the module.

## [0.25.0] - 2022-12-07

### Breaking changes

- `decorators.pass_app_context` is now keyword only (removes deprecation from previous version).

## [0.24.0] - 2022-12-07

### Fixes

- Reference to disabled commands.

### Deprecated

- `decorators.pass_app_context` will pass a named argument defaulting to `app_context` instead of a positional argument to the decorated function. This allows the decorator position to be independent on the function argument. The argument name is changeable.

  If you get a warning `TypeError: <FUNCTION> got multiple values for argument 'app_context'`, this is likely caused by the `@click.pass_context` decorator, which is positional, and it's argument must match the position.

## [0.23.1] - 2022-11-30

### Fixes

- Make `models.AppContext` generic to allow specifying `models.PluginConfig` subclasses in plugins.

## [0.23.0] - 2022-11-30

### Deprecated

- Moved (change import statement):
  - `contexts.AppContext`. Use `models.AppContext`.
  - `contexts.pass_app_context`. Use `decorators.pass_app_context`

- Changed functionality:
  - `click_utils.filepaths_argument`. Use `decorators.files_folders` instead.

### Features

- `decorators.pass_args` decorator to allow pass-through arguments in commands. Command receives them as a `passed_args` argument.
- `decorators.files_folders_option` decorator, which implements a `-f`/`--file`/`--folder` option to supply command with files and/or folders. It can be used multiple times. The command receives this as a `files_folders` argument. Introduced to resolve a conflict with `decorators.pass_args`.

## [0.22.0] - 2022-11-30

### Breaking changes

- All optional dependencies (a.k.a. extras) except for `completion` have been moved to the plugin `delfino-core`. To migrate, move the `extras` of `delfino` to `delfino-core`.
- Revert to loading commands in plugins only from given entry point.

## [0.21.0] - 2022-11-29

### Breaking changes

- Removed `tasks` folder as a fallback for `commands`, containing local Click commands.
- Removed built-in commands. Please install [delfino-core](https://github.com/radeklat/delfino-core) instead.
- The following configuration options changed their location from `tool.delfino.<OPTION>` to `tool.delfino.plugins.delfino-core.<OPTION>`:
  - `disable_commands`
  - `sources_directory`
  - `tests_directory`
  - `reports_directory`
  - `test_types`
  - `verify_commands`
  - `disable_pre_commit`
  - `dockerhub`
  - `typecheck`

### Features

- Instances of `click.Command` are discovered recursively rather than just in the top level files.
- Local folder with commands can be overriden from the default `commands` with a `tool.delfino.local_commands_directory` configuration option in the `pyproject.toml` file.

## [0.20.3] - 2022-11-26

### Fixes

- Fix `importlib.metadata` import.

## [0.20.2] - 2022-11-26

### Fixes

- Fix `importlib` deprecation.

## [0.20.1] - 2022-11-26

### Fixes

- Load commands from `__init__.py` files in plugins.

## [0.20.0] - 2022-11-16

### Features

- Plugin support. Now commands can also be loaded from installed packages.

### Deprecated

- ```
  [tool.delfino]
  disable_commands = [<COMMAND>]
  ```
  configuration option in favour of
  ```
  [tool.delfino.plugins.core]
  disable_commands = [<COMMAND>]
  ```
  Note that the name `core` of the plugin may change in the future.

## [0.19.1] - 2022-11-11

### Fixes

- Add trove classifiers for Pypi.

## [0.19.0] - 2022-11-11

### Breaking changes

- Minimum supported Python version increased from 3.7.0 to 3.7.2 (required by `pylint`).

### Features

- Maximum supported Python version increased to 3.11.

### Fixes

- Missing `Optional` type annotation, mandated by PEP 484.

## [0.18.2] - 2022-10-25

### Fixes

- Correct number of job used by pylint in CI.

## [0.18.1] - 2022-10-11

### Fixes

- Correct number of job used by pylint.

## [0.18.0] - 2022-09-13

### Features

- Add "strict_directories" config for the typecheck command.
- Add path argument to the typecheck command.

### Fixes

- Fix typo in the test command header message.

## [0.17.1] - 2022-09-12

### Fixes

- Replace a magic constant.

## [0.17.0] - 2022-09-02

### Features

- Lint/typecheck/format commands will be applied to the "commands" directory if exists.

## [0.16.1] - 2022-09-01

### Fixes

- Fix AttributeError when executing verify-all command.

## [0.16.0] - 2022-08-23

### Features

- Configuration now supports a `disable_pre_commit` flag. If set, pre-commit integration is disabled.

## [0.15.0] - 2022-08-23

### Features

- A new configuration field `verify_commands` can be configured to fine-tune which commands are run as part of `verify-all`

### Features

- The `verify-all` command now respects overridden commands and disabled commands

## [0.14.0] - 2022-07-08

### Features

- `lint-pylint` uses maximum number of available CPU cores to speed up execution.

### Fixes

- Dependencies update

## [0.13.1] - 2022-07-06

### Fixes
- 
- `build-docker --serialized` also serializes emulators installation.

## [0.13.0] - 2022-01-28

### Features

- `--log-level` option to set logging level globally.

### Features

- Disabled commands show up in help only in the DEBUG log level.

## [0.12.2] - 2022-01-28

### Fixes

- Delfino swallowing `ModuleNotFound` exceptions in auto-discovered commands.

## [0.12.1] - 2022-01-28

### Fixes

- Tests not correctly filtered on their test type if the `--debug` flag is omitted.

## [0.12.0] - 2022-01-26

### Features

- `--serialized` option to `build-docker` command to prevent parallelized build of multiple platforms.

### Fixes

- Presence of `pyproject.toml` or know package manager is no longer required when running without arguments or with `-h`/`--help`.

## [0.11.0] - 2021-12-10

### Features

- Completion scripts are generated into a separate file.

## [0.10.0] - 2021-12-07

### Features

- `--show-completion` and `--install-completion` root parameters. Currently, only Bash is supported.
- Optional dependency `completion` to install `shellingham`, required by the new parameters.

## [0.9.0] - 2021-12-02

### Features

- Checks if optional Python packages in commands are installed.
- `-h` option as an alias for `--help` everywhere.
- Styling of disabled commands in help text.
- Rename `contexts.AppContext.py_project_toml` to `pyproject_toml`.

### Fixes

- Unhandled exception when unknown command used in command line.
- Auto-complete failing when `pyproject.toml` is not in the current working directory or is missing required fields.
- Removed dependency on `pytest-dotenv` and `pytest-mock` as they are not required by any of the commands.

## [0.8.1] - 2021-11-29

### Fixes

- `build-docker` passing Python version to the build incorrectly.

## [0.8.0] - 2021-11-29

### Features

- Command `upload-to-pypi` to push packages to Pypi using `twine`.
- `tool.delfino.disable_commands` option in `pyproject.toml` to disable commands not needed in the current project.

#### Command `build-docker`

To build and push multi-platform docker images.
Requires `tool.delfino.dockerhub` defined in `pyproject.toml`. Example:

```toml
username = "radeklat"
build_for_platforms = [
    "linux/amd64",
    "linux/arm64",
    "linux/arm/v7",
]
```

#### Validation support

Commands can raise `AssertionError` exceptions to tell `delfino` some pre-conditions haven't been met. It will be automatically translated into a `click.exceptions.Exit` exception and the exception string will be printed with the command name that has caused it.


## [0.7.1] - 2021-11-26

### Fixes

- Missing optional requirements.

## [0.7.0] - 2021-11-26

### Features

- Rename project to `delfino`.

## [0.6.0] - 2021-11-25

### Features

- Loading commands from local `tasks` module.

## [0.5.0] - 2021-11-25

### Breaking changes

- Drop support for Python 3.6.

### Features

- Commands are loaded as plugins dynamically.
- Split of `utils` into more focused modules.

## [0.4.0] - 2021-11-23

### Breaking changes

- Dependency on `invoke` (replaced with `subprocess.run`) and `termcolor` (replaced with `click.secho`).

### Features

- Icon to `typecheck` header.
- Reversing right icon in header if it has more than 1 emoji.
- `switch-python-version` detects if package manager is not installed and installs it if not.

## [0.3.1] - 2021-11-22

### Fixes

- Reference to the tool's entry point move to a constant instead of reading it from `pyproject.toml` (which is not distributed with the package).

## [0.3.0] - 2021-11-21

### Features

- Detect package manager (currently only `poetry` and `pipenv`)

## [0.2.0] - 2021-11-21

### Features

- `extras` dependencies in `pyproject.toml`
- `init` command to initialize required parameters and directories.

### Features

- Rename project to `rads-toolbox` to be able to publish to Pypi.
- Package publishing from GitHub releases to Pypi.

## [0.1.0] - 2021-11-20

- Initial copy of source codes.

[Unreleased]: https://github.com/radeklat/delfino/compare/5.0.0...HEAD
[5.0.0]: https://github.com/radeklat/delfino/compare/4.0.0...5.0.0
[4.0.0]: https://github.com/radeklat/delfino/compare/3.1.2...4.0.0
[3.1.2]: https://github.com/radeklat/delfino/compare/3.1.1...3.1.2
[3.1.1]: https://github.com/radeklat/delfino/compare/3.1.0...3.1.1
[3.1.0]: https://github.com/radeklat/delfino/compare/3.0.2...3.1.0
[3.0.2]: https://github.com/radeklat/delfino/compare/3.0.1...3.0.2
[3.0.1]: https://github.com/radeklat/delfino/compare/3.0.0...3.0.1
[3.0.0]: https://github.com/radeklat/delfino/compare/2.0.0...3.0.0
[2.0.0]: https://github.com/radeklat/delfino/compare/1.3.0...2.0.0
[1.3.0]: https://github.com/radeklat/delfino/compare/1.2.0...1.3.0
[1.2.0]: https://github.com/radeklat/delfino/compare/1.1.1...1.2.0
[1.1.1]: https://github.com/radeklat/delfino/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/radeklat/delfino/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/radeklat/delfino/compare/0.30.0...1.0.0
[0.30.0]: https://github.com/radeklat/delfino/compare/0.29.0...0.30.0
[0.29.0]: https://github.com/radeklat/delfino/compare/0.28.1...0.29.0
[0.28.1]: https://github.com/radeklat/delfino/compare/0.28.0...0.28.1
[0.28.0]: https://github.com/radeklat/delfino/compare/0.27.0...0.28.0
[0.27.0]: https://github.com/radeklat/delfino/compare/0.26.1...0.27.0
[0.26.1]: https://github.com/radeklat/delfino/compare/0.26.0...0.26.1
[0.26.0]: https://github.com/radeklat/delfino/compare/0.25.0...0.26.0
[0.25.0]: https://github.com/radeklat/delfino/compare/0.24.0...0.25.0
[0.24.0]: https://github.com/radeklat/delfino/compare/0.23.1...0.24.0
[0.23.1]: https://github.com/radeklat/delfino/compare/0.23.0...0.23.1
[0.23.0]: https://github.com/radeklat/delfino/compare/0.22.0...0.23.0
[0.22.0]: https://github.com/radeklat/delfino/compare/0.21.0...0.22.0
[0.21.0]: https://github.com/radeklat/delfino/compare/0.20.3...0.21.0
[0.20.3]: https://github.com/radeklat/delfino/compare/0.20.2...0.20.3
[0.20.2]: https://github.com/radeklat/delfino/compare/0.20.1...0.20.2
[0.20.1]: https://github.com/radeklat/delfino/compare/0.20.0...0.20.1
[0.20.0]: https://github.com/radeklat/delfino/compare/0.19.1...0.20.0
[0.19.1]: https://github.com/radeklat/delfino/compare/0.19.0...0.19.1
[0.19.0]: https://github.com/radeklat/delfino/compare/0.18.2...0.19.0
[0.18.2]: https://github.com/radeklat/delfino/compare/0.18.1...0.18.2
[0.18.1]: https://github.com/radeklat/delfino/compare/0.18.0...0.18.1
[0.18.0]: https://github.com/radeklat/delfino/compare/0.17.1...0.18.0
[0.17.1]: https://github.com/radeklat/delfino/compare/0.17.0...0.17.1
[0.17.0]: https://github.com/radeklat/delfino/compare/0.16.1...0.17.0
[0.16.1]: https://github.com/radeklat/delfino/compare/0.16.0...0.16.1
[0.16.0]: https://github.com/radeklat/delfino/compare/0.15.0...0.16.0
[0.15.0]: https://github.com/radeklat/delfino/compare/0.14.0...0.15.0
[0.14.0]: https://github.com/radeklat/delfino/compare/0.13.1...0.14.0
[0.13.1]: https://github.com/radeklat/delfino/compare/0.13.0...0.13.1
[0.13.0]: https://github.com/radeklat/delfino/compare/0.12.2...0.13.0
[0.12.2]: https://github.com/radeklat/delfino/compare/0.12.1...0.12.2
[0.12.1]: https://github.com/radeklat/delfino/compare/0.12.0...0.12.1
[0.12.0]: https://github.com/radeklat/delfino/compare/0.11.0...0.12.0
[0.11.0]: https://github.com/radeklat/delfino/compare/0.10.0...0.11.0
[0.10.0]: https://github.com/radeklat/delfino/compare/0.9.0...0.10.0
[0.9.0]: https://github.com/radeklat/delfino/compare/0.8.1...0.9.0
[0.8.1]: https://github.com/radeklat/delfino/compare/0.8.0...0.8.1
[0.8.0]: https://github.com/radeklat/delfino/compare/0.7.1...0.8.0
[0.7.1]: https://github.com/radeklat/delfino/compare/0.7.0...0.7.1
[0.7.0]: https://github.com/radeklat/delfino/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/radeklat/delfino/compare/0.5.0...0.6.0
[0.5.0]: https://github.com/radeklat/delfino/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/radeklat/delfino/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/radeklat/delfino/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/radeklat/delfino/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/radeklat/delfino/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/radeklat/delfino/compare/initial...0.1.0
