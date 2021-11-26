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

[Unreleased]: https://github.com/radeklat/settings-doc/compare/0.7.0...HEAD
[0.7.0]: https://github.com/radeklat/settings-doc/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/radeklat/settings-doc/compare/0.5.0...0.6.0
[0.5.0]: https://github.com/radeklat/settings-doc/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/radeklat/settings-doc/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/radeklat/settings-doc/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/radeklat/settings-doc/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/radeklat/settings-doc/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/radeklat/settings-doc/compare/initial...0.1.0