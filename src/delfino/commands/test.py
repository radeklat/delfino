"""Tests on source code."""

import re
import shutil
import warnings
import webbrowser
from pathlib import Path
from subprocess import PIPE

import click
from deprecation import DeprecatedWarning

from delfino.click_utils._wrapper_command import wrapper_command
from delfino.contexts import AppContext, pass_app_context
from delfino.execution import OnError, run
from delfino.terminal_output import print_header, run_command_example
from delfino.utils import ArgsList, ensure_reports_dir
from delfino.validation import assert_pip_package_installed


def _run_tests(app_context: AppContext, click_context: click.Context, name: str, debug) -> None:
    """Execute the tests for a given test type."""
    for pkg in ("pytest", "pytest-cov", "coverage"):
        assert_pip_package_installed(pkg)

    delfino = app_context.pyproject_toml.tool.delfino

    if name not in delfino.test_types or not delfino.tests_directory:
        return

    print_header(f"️Running {name} tests️", icon="🔎🐛")
    ensure_reports_dir(delfino)

    options: ArgsList = []
    if debug:
        options.append("--capture=no")
        warnings.warn(
            DeprecatedWarning(
                "--debug for test-unit and test-integration command",
                "0.19.0",
                "1.0.0",
                "Use --capture=no or -s instead.",
            )
        )

    args: ArgsList = [
        "pytest",
        "--cov",
        delfino.sources_directory,
        "--cov-report",
        f"xml:{delfino.reports_directory / f'coverage-{name}.xml'}",
        "--cov-branch",
        "-vv",
        *options,
        *click_context.args,
        delfino.tests_directory / name,
    ]
    run(
        args,
        env_update={"COVERAGE_FILE": delfino.reports_directory / f"coverage-{name}.dat"},
        on_error=OnError.ABORT,
    )


def test_options(func):
    """Common option for test commands."""
    click.option(
        "--debug",
        is_flag=True,
        help=(
            "Deprecated. Use --capture=no or -s instead."
            " | Disables capture, allowing debuggers like `pdb` to be used."
        ),
    )(func)
    return func


@wrapper_command("mypy", help="Run unit tests.")
@test_options
@pass_app_context
def test_unit(app_context: AppContext, click_context: click.Context, debug: bool):
    _run_tests(app_context, click_context, "unit", debug)


@wrapper_command("mypy", help="Run integration tests.")
@test_options
@pass_app_context
def test_integration(app_context: AppContext, click_context: click.Context, debug):
    # TODO(Radek): Replace with alias?
    _run_tests(app_context, click_context, "integration", debug)


def _get_total_coverage(coverage_dat: Path) -> str:
    """Return coverage percentage, as captured in coverage dat file; e.g., returns "100%"."""
    output = run(
        "coverage report", stdout=PIPE, env_update={"COVERAGE_FILE": coverage_dat}, on_error=OnError.EXIT
    ).stdout.decode()
    match = re.search(r"TOTAL.*?([\d.]+%)", output)
    if match is None:
        raise RuntimeError(f"Regex failed on output: {output}")
    return match.group(1)


@click.command()
@pass_app_context
def coverage_report(app_context: AppContext):
    """Analyse coverage and generate a term/HTML report.

    Combines all test types.
    """
    assert_pip_package_installed("coverage")

    print_header("Generating coverage report", icon="📃")
    delfino = app_context.pyproject_toml.tool.delfino
    ensure_reports_dir(delfino)

    coverage_dat_combined = delfino.reports_directory / "coverage.dat"
    coverage_html = delfino.reports_directory / "coverage-report/"
    coverage_files = []  # we'll make a copy because `combine` will erase them

    for test_type in delfino.test_types:
        coverage_dat = delfino.reports_directory / f"coverage-{test_type}.dat"

        if not coverage_dat.exists():
            click.secho(
                f"Could not find coverage dat file for {test_type} tests: {coverage_dat}",
                fg="yellow",
            )
        else:
            print(f"{test_type.title()} test coverage: {_get_total_coverage(coverage_dat)}")

            temp_copy = coverage_dat.with_name(coverage_dat.name.replace(".dat", "-copy.dat"))
            shutil.copy(coverage_dat, temp_copy)
            coverage_files.append(temp_copy)

    env = {"COVERAGE_FILE": coverage_dat_combined}
    run(["coverage", "combine", *coverage_files], env_update=env, stdout=PIPE, on_error=OnError.EXIT)
    run(["coverage", "html", "-d", coverage_html], env_update=env, stdout=PIPE, on_error=OnError.EXIT)

    print(f"Total coverage: {_get_total_coverage(coverage_dat_combined)}\n")
    print(
        f"Refer to coverage report for full analysis in '{coverage_html}/index.html'\n"
        f"Or open the report in your default browser with:\n"
        f"  {run_command_example(coverage_open, app_context)}"
    )


@click.command(help="Run all tests, and generate coverage report.")
@click.pass_context
def test_all(click_context: click.Context):
    print_header("Run all tests, and generate coverage report.", icon="🔎🐛📃")
    click_context.forward(test_unit)
    click_context.forward(test_integration)
    click_context.forward(coverage_report)


@click.command(help="Open coverage results in default browser.")
@pass_app_context
def coverage_open(app_context: AppContext):
    report_index = app_context.pyproject_toml.tool.delfino.reports_directory / "coverage-report" / "index.html"
    if not report_index.exists():
        click.secho(
            f"Could not find coverage report '{report_index}'. Ensure that the report has been built.\n"
            "Try one of the following:\n"
            f"  {run_command_example(coverage_report, app_context)}\n"
            f"or\n"
            f"  {run_command_example(test_all, app_context)}",
            fg="red",
        )

        raise click.exceptions.Exit(code=1)
    webbrowser.open(f"file:///{report_index.absolute()}")
