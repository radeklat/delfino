<h1 align="center" style="border-bottom: none;">🧰&nbsp;&nbsp;Delfino&nbsp;&nbsp;🧰</h1>
<h3 align="center">A collection of command line helper scripts wrapping tools used during Python development.</h3>

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
    <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2022">
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

<!--
    How to generate TOC from PyCharm:
    https://github.com/vsch/idea-multimarkdown/wiki/Table-of-Contents-Extension
-->
[TOC levels=1,2 markdown formatted bullet hierarchy]: # "Table of content"

# Table of content
- [Installation](#installation)
  - [Optional dependencies](#optional-dependencies)
- [Usage](#usage)
  - [Auto-completion](#auto-completion)
- [Development](#development)
  - [Minimal command](#minimal-command)

# Installation

- pip: `pip install delfino`
- Poetry: `poetry add -D delfino`
- Pipenv: `pipenv install -d delfino`

or 

- pip: `pip install delfino[completion]`
- Poetry: `poetry add -D delfino[completion]`
- Pipenv: `pipenv install -d delfino[completion]`

to enable [auto-completion](#auto-completion).

## Optional dependencies

Each project may use different sub-set of commands. Therefore, dependencies of all commands are optional and checked only when the command is executed.

Using `[all]` installs all the [optional dependencies](https://setuptools.pypa.io/en/latest/userguide/dependency_management.html#optional-dependencies) used by all the built-in commands. If you want only a sub-set of those dependencies, there are finer-grained groups available:

- For top-level parameters:
  - `completion` - for `--show-completion` and `--install-completion`
- For individual commands (matches the command names):
  - `upload_to_pypi`
  - `build_docker`
  - `typecheck`
  - `format`
- For groups of commands:
  - `test` - for testing and coverage commands
  - `lint` - for all the linting commands
- For groups of groups:
  - `verify_all` - same as `[typecheck,format,test,lint]`
  - `all` - all optional packages

## Configuration

Delfino will assume certain project structure. However, you can customize it to match your own by overriding the default values in the `pyproject.toml` file. Here are the defaults that you can modify:

```toml
[tool.delfino]
reports_directory = "reports"
sources_directory = "src"
tests_directory = "tests"
local_commands_directory = "commands"
test_types = ["unit", "integration"]
verify_commands = ["format", "lint", "typecheck", "test-all"]
disable_pre_commit = false

[tool.delfino.typecheck]
strict_directories = ['src']

# By default, all commands will be enabled. Use `enable_commands` or `disable_commands` 
# to show only a subset of commands. If both used, disabled commands are subtracted 
# from the set of enabled commands. 
# [tool.delfino.plugins.<PLUGIN_NAME_A>]
# enable_commands = [<COMMAND_NAME>]
# disable_commands = [<COMMAND_NAME>]
# [tool.delfino.plugins.<PLUGIN_NAME_B>]
# enable_commands = [<COMMAND_NAME>]
# disable_commands = [<COMMAND_NAME>]

# You can pass additional arguments to commands per project
# See https://github.com/radeklat/delfino/blob/main/src/delfino/commands/pass_args.py for usage.
# [tool.delfino.plugins.<PLUGIN>.<COMMAND>]
# pass_args = '--capture=no'

[tool.delfino.dockerhub]
username = ""
build_for_platforms = [
    "linux/amd64",
    "linux/arm64",
    "linux/arm/v7",
]
```

# Usage

Run `delfino --help` to see all available commands and their usage.

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

# Development

Delfino is a simple wrapper around [Click](https://click.palletsprojects.com). It allows you to add custom, project-specific [commands](https://click.palletsprojects.com/en/8.0.x/quickstart/#basic-concepts-creating-a-command). Let's call them Delfino commands or just commands. Commands are expected in the root of the project, in a Python package called `commands`. Any sub-class of [`click.Command`](https://click.palletsprojects.com/en/8.0.x/api/#click.Command) in any `.py` file in this folder will be automatically used by Delfino.

## Minimal command

<!-- TODO(Radek): Delfino expects `pyproject.toml` configured. -->
<!-- TODO(Radek): Delfino expects Poetry or Pipenv to be available. -->

1. Create the `commands` package:
   ```shell script
   mkdir commands
   touch commands/__init__.py
   ```
2. Create a file `commands/command_test.py`, with the following content:
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

<!--
## Advanced Command

Delfino adds optional bits of functionality on top of Click. The following example demonstrates some of those:

```python
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
