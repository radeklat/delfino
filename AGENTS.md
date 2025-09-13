# Project Overview

This project is a CLI application that discovers and exposes Click commands from pre-defined locations and other delfino plugins. It provides a unified interface for managing and executing commands.

# Technologies
- Languages: Python 3.9-3.13
- Testing: pytest, pytest.mark.parametrize, pytest-mock, pytest fixtures, pytest-httpx (https://colin-b.github.io/pytest_httpx/)
- Dependency management: uv
- CI/CD: CircleCI

# Code Structure
├── CHANGELOG.md - changelog for the project.
├── dist - distribution files for the package.
├── documentation - documentation files for thing that do not fit into the top level README.md.
├── LICENSE - license file for the project.
├── poetry.lock - Poetry lock file for dependency management.
├── poetry.toml - Poetry configuration file.
├── pyproject.toml - Poetry project configuration file.
├── README.md - main README file for the project.
├── reports - generated reports and documentation.
├── src - source code of the project.
└── tests - automated testing suite that uses pytest.
    ├── integration - integration tests.
    └── unit - unit tests.

# Coding Conventions
1. Use Pydantic models for data validation and serialization
2. Follow type hints throughout the codebase
3. Use async/await for asynchronous operations
4. Use dependency injection where appropriate

# Logging
1. Use Python's built-in logging module for structured logging. Create a logger in each module as `logger = logging.getLogger(__name__)`.
2. Use the following logging levels:
   - `DEBUG` for detailed debugging information, not to be used in production.
   - `INFO` for general operational messages. Should not be logged more than once per second.
   - `WARNING` for fixable issues and possible data inconsistencies that do not stop the application.
   - `ERROR` for errors and clear data inconsistencies that require attention, but do not stop the application.
   - `CRITICAL` for critical errors that stop the application. Must be logged into Sentry as well.
3. Log messages with appropriate context information, such as request IDs, and operation details.

# Documentation
1. Keep README.md up to date
2. Document changes in CHANGELOG.md in the "Unreleased" section.

# Development Workflow
1. Use `uv run <COMMAND>` to run commands in the virtual environment
2. Use `delfino verify` for linting and formatting
3. Write comprehensive tests for new features

# Type annotations
Use Python 3.9 type annotations:
- Dict -> dict
- List -> list
- Generator[None, None, None] -> Iterator[None]
- Final[...] for constants

Use library-specific types where applicable, e.g.:
- `mocker: MockerFixture` (`from pytest_mock import MockerFixture`)
- `httpx_mock: HTTPXMock` (`from pytest_httpx import HTTPXMock`)
- `caplog: LogCaptureFixture` (`from pytest import LogCaptureFixture`)

# Testing Guidelines
1. Write unit tests for functions and classes
2. Write integration tests for commands
3. Use pytest fixtures for test setup
4. Use parameterized tests with `pytest.mark.parametrize` for testing multiple scenarios
5. Use `pytest.param(.., id="test name")` to label parameterized tests with custom names
6. Mock external dependencies in unit tests

## Tests signposting
Use "GIVEN/WHEN/THEN/AND <DESCRIPTION>" comments to annotate setup, test and checks. For example:

```python
# GIVEN event happens

# WHEN it is processed by the endpoint

# THEN a Slack message is sent

# AND success response is sent back
```

# Making a release
1. Update the "Unreleased" section in CHANGELOG.md
2. Based on the changes, run `poetry version major/minor/patch` to update the version in pyproject.toml based on the changes (breaking changes = major, features = minor, fixes = patch).
3. Update the "Unreleased" section in CHANGELOG.md to the new version with today's date.
4. Commit the changes in a new branch called "release/$(uv version --short)" with a message "Release X.Y.Z".
5. Push the branch to the remote repository.