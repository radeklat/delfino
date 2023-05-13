<h1 align="center" style="border-bottom: none;">🧰&nbsp;&nbsp;Delfino&nbsp;&nbsp;🧰</h1>
<h3 align="center">The Ultimate Command Line Companion for Your Projects</h3>

<p align="center">
    <a href="https://app.circleci.com/pipelines/github/radeklat/delfino?branch=main">
        <img alt="CircleCI" src="https://img.shields.io/circleci/build/github/radeklat/delfino">
    </a>
    <a href="https://app.codecov.io/gh/radeklat/delfino/">
        <img alt="Codecov" src="https://img.shields.io/codecov/c/github/radeklat/delfino">
    </a>
    <a href="https://github.com/radeklat/delfino/tags">
        <img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/tag/radeklat/delfino">
    </a>
    <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2023">
    <a href="https://github.com/radeklat/delfino/commits/main">
        <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/radeklat/delfino">
    </a>
    <a href="https://www.python.org/doc/versions/">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/delfino">
    </a>
    <a href="https://pypistats.org/packages/delfino">
        <img alt="Downloads" src="https://img.shields.io/pypi/dm/delfino">
    </a>
</p>

Tired of managing scattered scripts? Say goodbye to complexity with Delfino!

Delfino is a powerful wrapper around Click, the popular command line interface package. It automatically discovers and executes Click commands in your project. But Delfino doesn't stop there - it takes it a step further by allowing you to create plugins, making script distribution and installation a breeze.

# Why choose Delfino?

- **Streamline Scripts**: Consolidate all your helper scripts into a single, easy-to-use entry point. No more hunting for scripts or dealing with convoluted aliases. Simply use delfino followed by the script name and options.
- **Reusable Plugins**: Package your helper scripts as plugins and install them with pip. Maintain consistency across projects and easily incorporate updates through a flexible configuration system.
- **Simplify Tooling**: Delfino extends Click with advanced features like pass-through command-line options and seamless handling of file lists. Say goodbye to verbosity and hello to optimized workflows.

Don't let scattered scripts and complex tooling slow you down. Embrace Delfino and revolutionize your command line experience. Try Delfino today and unlock simplicity in your projects!

<!--
    How to generate TOC from PyCharm:
    https://github.com/vsch/idea-multimarkdown/wiki/Table-of-Contents-Extension
-->
[TOC levels=1,2 markdown formatted bullet hierarchy]: # "Table of content"

# Table of content
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
  - [Commands discovery](#commands-discovery)
  - [Minimal command](#minimal-command)
  - [Minimal plugin](#minimal-plugin)
- [Existing plugins](#existing-plugins)
  - [Enabling a plugin](#enabling-a-plugin)
  - [Enabling/disabling commands](#enablingdisabling-commands)
- [Advanced usage](#advanced-usage)
  - [Auto-completion](#auto-completion)
  - [Running external programs](#running-external-programs)
  - [Optional dependencies](#optional-dependencies)
  - [Project settings](#project-settings)
  - [Plugin settings](#plugin-settings)
  - [Project specific overrides](#project-specific-overrides)
  - [Grouping commands](#grouping-commands)

# Installation

- pip: `pip install delfino`
- Poetry: `poetry add --group=dev delfino`
- Pipenv: `pipenv install -d delfino`

or 

- pip: `pip install delfino[completion]`
- Poetry: `poetry add --group=dev delfino[completion]`
- Pipenv: `pipenv install -d delfino[completion]`

to enable [auto-completion](#auto-completion).

# Configuration

All configuration is expected to live in one of the following files:

- `pyproject.toml` in the project root
- `.delfinorc` in the project root - to allow dev specific config, not source controlled or for non-Python projects
- `.delfinorc` in the user home directory - for user tools available in the system

If multiple files are discovered, only the highest one in the list will be used.

The format for `.delfinorc` is the same as for `pyproject.toml`.

# Usage

Run `delfino --help` to see all available commands and their usage.

# Development

Delfino is a simple wrapper around [Click commands](https://click.palletsprojects.com/quickstart/#basic-concepts-creating-a-command). Any Click command will be accepted by Delfino.

## Commands discovery

Delfino looks for any [`click.Command`](https://click.palletsprojects.com/en/8.0.x/api/#click.Command) sub-class in the following locations:

- `commands` folder in the root of the project (next to the `pyproject.toml` file). This location is useful for commands that don't need to be replicated in multiple locations/projects. To change the default location, use the `tool.delfino.local_command_folders` config option. It allows specifying more than one folder.
- python module import path (`<IMPORT_PATH>`) specified by `entry_point` of [a plugin](#minimal-plugin):
  ```toml
  [tool.poetry.plugins] # Optional super table

  [tool.poetry.plugins."delfino.plugin"]
  "delfino-<PLUGIN_NAME>" = "<IMPORT_PATH>"
  ```
- Folder specified in the [config file](#configuration) under `tool.delfino.local_commands_directory`.

Any files starting with an underscore, except for `__init__.py`, will be ignored.

> **Warning**
> Folders are NOT inspected recursively. If you place any commands into nested folders, they will not be loaded by Delfino.


## Minimal command

<!-- TODO(Radek): Delfino expects `pyproject.toml` configured. -->
<!-- TODO(Radek): Delfino expects Poetry or Pipenv to be available. -->

1. Create a `commands` folder:
   ```shell script
   mkdir commands
   ```
2. Create a `commands/__init__.py` file, with the following content:
   ```python
   import click
   
   @click.command()
   def command_test():
       """Tests commands placed in the `commands` folder are loaded."""
       print("✨ This command works! ✨")
   ```
3. See if Delfino loads the command. Open a terminal and in the root of the project, call: `delfino --help`. You should see something like this:
   ```text
   Usage: delfino [OPTIONS] COMMAND [ARGS]...
   
   Options:
     --help  Show this message and exit.
   
   Commands:
     ...
     command-test            Tests commands placed in the `commands` folder...
     ...
   ```
4. Run the command with `delfino command-test`

## Minimal plugin

If you'd like to use one or more commands in multiple places, you can create a plugin. A plugin is just a regular Python package with specific entry point telling Delfino it should use it. It can also be distributed as any other Python packages, for example via Pypi.

The quickest way to create one is to use a [Delfino plugin cookiecutter template](https://github.com/radeklat/delfino-plugin-cookiecutter-template), which asks you several questions and sets up the whole project.

Alternatively, you can get inspired by [the demo plugin](https://github.com/radeklat/delfino-demo) or any of the other [existing plugins](#plugins).

# Existing plugins

Plugins can greatly reduce code duplication and/or promote your own standards in multiple places. For example, you can create a plugin wrapping common linting tools that you use on your projects, including their default configuration. Keeping the rules and creating new projects with the same style suddenly becomes a matter of installing one Python library.

Each plugin can contain one or more Click commands that are automatically discovered and exposed by Delfino. See [`delfino-demo`](https://github.com/radeklat/delfino-demo) for a minimal plugin, which provide a `demo` command printing out a message.

Existing plugins:

| Plugin name                                                  | Description                                                                                        |
|:-------------------------------------------------------------|:---------------------------------------------------------------------------------------------------|
| [delfino-demo](https://github.com/radeklat/delfino-demo)     | A minimal plugin example for Delfino. Contains one command printing a message.                     |
| [delfino-core](https://github.com/radeklat/delfino-core)     | Commands wrapping tools used during every day development (linting, testing, dependencies update). |
| [delfino-docker](https://github.com/radeklat/delfino-docker) | Docker build helper script.                                                                        |

## Enabling a plugin

For security reasons, plugins are disabled by default. To enable a plugin, you have to include it in the `pyproject.toml` file:

```toml
[tool.delfino.plugins.<PLUGIN_NAME>]
```

## Enabling/disabling commands

By default, all commands are enabled. Use `enable_commands` or `disable_commands`  to show only a subset of commands. If both used, disabled commands are subtracted from the set of enabled commands.

```toml
# [tool.delfino.plugins.<PLUGIN_NAME_A>]
# enable_commands = [<COMMAND_NAME>]
# disable_commands = [<COMMAND_NAME>]

# [tool.delfino.plugins.<PLUGIN_NAME_B>]
# enable_commands = [<COMMAND_NAME>]
# disable_commands = [<COMMAND_NAME>]
```

# Advanced usage

<!--
## Advanced Command

Delfino adds optional bits of functionality on top of Click. The following example demonstrates some of those:

```python
# commands/__init__.py

import click

from delfino.contexts import pass_app_context, AppContext
from delfino.validation import assert_pip_package_installed, pyproject_toml_key_missing

@click.command()
# The `pass_app_context` decorator adds `AppContext` as the first parameter.
@pass_app_context
def command_test(app_context: AppContext):
   """Tests commands placed in the `commands` folder are loaded."""
   # Test optional dependencies. Any failing assertion will be printed as:
   # Command '<NAME>' is misconfigured. <ASSERTION ERROR MESSAGE>
   assert_pip_package_installed("delfino")

   # AppContext contain a parsed `pyproject.toml` file.
   # Commands can add their config under `[tool.delfino.commands.<COMMAND_NAME>]`.
   assert "command_test" in app_context.pyproject_toml.tool.delfino.commands, \
       pyproject_toml_key_missing("tool.delfino.commands.command_test")

   print(app_context.pyproject_toml.tool.delfino.commands["command-test"])
```
-->

## Auto-completion

You can either attempt to install completions automatically with:

```shell script
delfino --install-completion
```

or generate it with:

```shell script
delfino --show-completion
```

and manually put it in the relevant RC file.

The auto-completion implementation is dynamic so that every time it is invoked, it uses the current project. Each project can have different commands or disable certain commands it doesn't use. And dynamic auto-completion makes sure only the currently available commands will be suggested.

The downside of this approach is that evaluating what is available each time is slower than a static list of commands.

## Running external programs

It is up to you how you want to execute external processes as part of commands (if you need to at all). A common way in Python is to use `subprocess.run`. Delfino comes with its own [`run` implementation](https://github.com/radeklat/delfino/blob/main/src/delfino/execution.py#L94), which wraps and simplifies `subprocess.run` for the most common use cases:

- Normalizing `subprocess.run` arguments - you can pass in either a string or a list. Either way, `subprocess.run` will be executed correctly.
- Handling errors from the execution via the `on_error` argument. Giving the option to either ignore the errors and continue (`PASS`), not continue and clean exit (`EXIT`) or not continue and abort with error code (`ABORT`).
- Setting environment variables.
- Logging what is being executed in the debug level.

Example:

```python
# commands/__init__.py

import click
from delfino.execution import run, OnError

@click.command()
def test():
    run("pytest tests", on_error=OnError.ABORT)
```

## Optional dependencies

If you put several commands into one [plugin](#plugins), you can make some dependencies of some commands [optional](https://python-poetry.org/docs/pyproject#extras). This is useful when a command is not always used, and you don't want to install unnecessary dependencies. Instead, you can check if a dependency is installed only when the command is executed with `delfino.validation.assert_pip_package_installed`:

```python
# commands/__init__.py

import click
from delfino.validation import assert_pip_package_installed

try:
    from git import Repo
except ImportError:
    pass

@click.command()
def git_active_branch():
    assert_pip_package_installed("gitpython")
    print(Repo(".").active_branch)
```

In the example above, if `gitpython` is not installed, delfino will show the command but will fail with suggestion to install `gitpython` only when the command is executed. You can also add `git_active_branch` into [`disable_commands` config](#enablingdisabling-commands) in places where you don't intend to use it.

This way you can greatly reduce the number of dependencies a plugin brings into a project without a need to have many small plugins.

## Project settings

You can store an arbitrary object in the Click context as [`click.Context.obj`](https://click.palletsprojects.com/api/#click.Context.obj). Delfino utilizes this object to store an instance of [`AppContext`](https://github.com/radeklat/delfino/blob/main/src/delfino/models/app_context.py), which provides access to project related information. If you need to, you can still attach arbitrary attributes to this object later.

You can pass this object to your commands by decorating them with [`click.pass_obj`](https://click.palletsprojects.com/api/#click.pass_obj):

```python
# commands/__init__.py

import click
from delfino.models.app_context import AppContext

@click.command()
@click.pass_obj
def print_app_version(obj: AppContext):
    print(obj.pyproject_toml.tool.poetry.version)
```

## Plugin settings

Plugin settings are expected to live in the `pyproject.toml` file. To prevent naming conflicts, each plugin must put its settings under `tool.delfino.plugins.<PLUGIN_NAME>`. It also allows Delfino to pass these settings directly to commands from these plugins.

Delfino loads, parses, validates and stores plugin settings in [`AppContext.plugin_config`](https://github.com/radeklat/delfino/blob/main/src/delfino/models/app_context.py). If not specified otherwise (see below), it will be an instance of [`PluginConfig`](https://github.com/radeklat/delfino/blob/main/src/delfino/models/pyproject_toml.py), with any extra keys unvalidated and in JSON-like Python objects.

You can add additional validation to your plugin settings by sub-classing the `PluginConfig` , defining expected keys, default values and/or validation. Delfino utilizes [`pydantic`](https://docs.pydantic.dev/) to create data classes.

Delfino also needs to know, which class to use for the validation. To do that, switch to `delfino.decorators.pass_app_context` instead of [`click.pass_obj`](https://click.palletsprojects.com/api/#click.pass_obj):

```toml
# pyproject.toml

[tool.delfino.plugins.delfino_login_plugin]
username = "user"
```

```python
# commands/__init__.py

import click
from delfino.models.pyproject_toml import PluginConfig
from delfino.models.app_context import AppContext
from delfino.decorators import pass_app_context


class LoginPluginConfig(PluginConfig):
    login: str


@click.command()
@pass_app_context(LoginPluginConfig)
def login(app_context: AppContext[LoginPluginConfig]):
    print(app_context.plugin_config.login)
```

The `AppContext` class is generic. Defining the `PluginConfigType` (such as `AppContext[LoginPluginConfig]` in the example above) enables introspection and type checks.

## Project specific overrides

It is likely your projects will require slight divergence to the defaults you encode in your scripts. The following sections cover the most common use cases.

### Pass-through arguments

You can pass additional arguments to downstream tools by decorating commands with the [`decorators.pass_args`](https://github.com/radeklat/delfino/blob/main/src/delfino/decorators/pass_args.py) decorator:

```python
# commands/__init__.py

from typing import Tuple

import click
from delfino.decorators import pass_args
from delfino.execution import run, OnError

@click.command()
@pass_args
def test(passed_args: Tuple[str, ...]):
    run(["pytest", "tests", *passed_args], on_error=OnError.ABORT)
```

Then additional arguments can be passed either via command line after `--`:

```shell script
delfino test -- --capture=no
```

Or via configuration in the `pyproject.toml` file:

```toml
[tool.delfino.plugins.<PLUGIN>.test]
pass_args = ['--capture=no']
```

Either way, both will result in executing `pytest tests --capture=no`.

### Files override

You can override files passed to downstream tools by decorating commands with the [`decorators.files_folders_option`](https://github.com/radeklat/delfino/blob/main/src/delfino/decorators/files_folders.py) decorator:

```python
# commands/__init__.py

from typing import Tuple

import click
from delfino.decorators import files_folders_option
from delfino.execution import run, OnError

@click.command()
@files_folders_option
def test(files_folders: Tuple[str, ...]):
    if not files_folders:
        files_folders = ("tests/unit", "tests/integration")
    run(["pytest", *files_folders], on_error=OnError.ABORT)
```

Then the default `"tests/unit", "tests/integration"` folders can be overridden either via command line options `-f`/`--file`/`--folder`:

```shell script
delfino test -f tests/other
```

Or via configuration in the `pyproject.toml` file:

```toml
[tool.delfino.plugins.<PLUGIN>.test]
files_folders = ['tests/other']
```

Either way, both will result in executing `pytest tests/other`.

## Grouping commands

Often it is useful to run several commands as a group with a different command name. Click supports calling other commands with [`click.Context.forward`](https://click.palletsprojects.com/api/#click.Context.forward) or [`click.Context.invoke`](https://click.palletsprojects.com/api/#click.Context.invoke).

<!-- TODO(Radek): Add description of `execute_commands_group` once migrated from `delfino-core`. -->
