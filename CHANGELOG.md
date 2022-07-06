# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).
Types of changes are:

- **Added** for new features.
- **Changed** for changes in existing functionality.
- **Deprecated** for soon-to-be removed features.
- **Removed** for now removed features.
- **Fixed** for any bug fixes.
- **Security** in case of vulnerabilities.

## [Unreleased]

## [0.13.1] - 2022-07-06

### Fixed

- `build-docker --serialized` also serializes emulators installation

## [0.13.0] - 2022-01-28

### Added

- `--log-level` option to set logging level globally.

### Changed

- Disabled commands show up in help only in the DEBUG log level.

## [0.12.2] - 2022-01-28

### Fixed

- Delfino swallowing `ModuleNotFound` exceptions in auto-discovered commands.

## [0.12.1] - 2022-01-28

### Fixed

- Tests not correctly filtered on their test type if the `--debug` flag is omitted.

## [0.12.0] - 2022-01-26

### Added

- `--serialized` option to `build-docker` command to prevent parallelized build of multiple platforms.

### Fixed

- Presence of `pyproject.toml` or know package manager is no longer required when running without arguments or with `-h`/`--help`.

## [0.11.0] - 2021-12-10

### Changed

- Completion scripts are generated into a separate file.

## [0.10.0] - 2021-12-07

### Added

- `--show-completion` and `--install-completion` root parameters. Currently, only Bash is supported.
- Optional dependency `completion` to install `shellingham`, required by the new parameters.

## [0.9.0] - 2021-12-02

### Added

- Checks if optional Python packages in commands are installed.
- `-h` option as an alias for `--help` everywhere.

### Changed

- Styling of disabled commands in help text.
- Rename `contexts.AppContext.py_project_toml` to `pyproject_toml`.

### Removed

- Dependency on `pytest-dotenv` and `pytest-mock` as they are not required by any of the commands.

### Fixed

- Unhandled exception when unknown command used in command line.
- Auto-complete failing when `pyproject.toml` is not in the current working directory or is missing required fields.

## [0.8.1] - 2021-11-29

### Fixed

- `build-docker` passing Python version to the build incorrectly.

## [0.8.0] - 2021-11-29

### Added

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

### Fixed

- Missing optional requirements.

## [0.7.0] - 2021-11-26

### Changed

- Rename project to `delfino`.

## [0.6.0] - 2021-11-25

### Added

- Loading commands from local `tasks` module.

## [0.5.0] - 2021-11-25

### Removed

- Drop support for Python 3.6.

### Changed

- Commands are loaded as plugins dynamically.
- Split of `utils` into more focused modules.

## [0.4.0] - 2021-11-23

### Removed

- Dependency on `invoke` (replaced with `subprocess.run`) and `termcolor` (replaced with `click.secho`).

### Added

- Icon to `typecheck` header.
- Reversing right icon in header if it has more than 1 emoji.
- `switch-python-version` detects if package manager is not installed and installs it if not.

## [0.3.1] - 2021-11-22

### Fixed

- Reference to the tool's entry point move to a constant instead of reading it from `pyproject.toml` (which is not distributed with the package).

## [0.3.0] - 2021-11-21

### Added

- Detect package manager (currently only `poetry` and `pipenv`)

## [0.2.0] - 2021-11-21

### Added

- `extras` dependencies in `pyproject.toml`
- `init` command to initialize required parameters and directories.

### Changed

- Rename project to `rads-toolbox` to be able to publish to Pypi.
- Package publishing from Github releases to Pypi.

## [0.1.0] - 2021-11-20

- Initial copy of source codes.

[Unreleased]: https://github.com/radeklat/settings-doc/compare/0.13.0...HEAD
[0.13.0]: https://github.com/radeklat/settings-doc/compare/0.12.2...0.13.0
[0.12.2]: https://github.com/radeklat/settings-doc/compare/0.12.1...0.12.2
[0.12.1]: https://github.com/radeklat/settings-doc/compare/0.12.0...0.12.1
[0.12.0]: https://github.com/radeklat/settings-doc/compare/0.11.0...0.12.0
[0.11.0]: https://github.com/radeklat/settings-doc/compare/0.10.0...0.11.0
[0.10.0]: https://github.com/radeklat/settings-doc/compare/0.9.0...0.10.0
[0.9.0]: https://github.com/radeklat/settings-doc/compare/0.8.1...0.9.0
[0.8.1]: https://github.com/radeklat/settings-doc/compare/0.8.0...0.8.1
[0.8.0]: https://github.com/radeklat/settings-doc/compare/0.7.1...0.8.0
[0.7.1]: https://github.com/radeklat/settings-doc/compare/0.7.0...0.7.1
[0.7.0]: https://github.com/radeklat/settings-doc/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/radeklat/settings-doc/compare/0.5.0...0.6.0
[0.5.0]: https://github.com/radeklat/settings-doc/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/radeklat/settings-doc/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/radeklat/settings-doc/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/radeklat/settings-doc/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/radeklat/settings-doc/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/radeklat/settings-doc/compare/initial...0.1.0