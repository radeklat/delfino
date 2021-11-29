from getpass import getpass
from os import getenv
from pathlib import Path
from typing import List

import click

from delfino.constants import PackageManager
from delfino.contexts import AppContext, pass_app_context
from delfino.execution import OnError, run
from delfino.terminal_output import print_header
from delfino.utils import ArgsList
from delfino.validation import assert_pip_package_installed, pyproject_toml_key_missing

try:
    from packaging.version import Version
except ImportError:
    pass


def _install_emulators(build_for_platforms: List[str]) -> None:
    """See https://github.com/tonistiigi/binfmt#installing-emulators."""
    emulators = []
    if "linux/arm64" in build_for_platforms:
        emulators.append("arm64")
    if "linux/arm/v7" in build_for_platforms:
        emulators.append("arm")

    if emulators:
        print_header("Installing emulators", level=2, icon="⬇")
        run(
            ["docker", "run", "--privileged", "--rm", "tonistiigi/binfmt", "--install", *emulators],
            on_error=OnError.EXIT,
        )


@click.command()
@click.option(
    "--push",
    is_flag=True,
    help="Push the built image and cache to remote docker image registry. Login is "
    "required and Personal Access Token will be requested from STDIN if "
    "`DOCKERHUB_PERSONAL_ACCESS_TOKEN` environment variable is not set.",
)
@pass_app_context
def build_docker(app_context: AppContext, push: bool):
    """Build and push a docker image."""
    delfino = app_context.py_project_toml.tool.delfino
    dockerfile = Path("Dockerfile")

    assert (
        app_context.package_manager == PackageManager.POETRY
    ), f"Only the '{PackageManager.POETRY.value}' package manager is supported by this command."
    assert_pip_package_installed("packaging")
    assert dockerfile.exists() and dockerfile.is_file(), "File 'Dockerfile' not found but required by this command."
    assert app_context.py_project_toml.tool.poetry, pyproject_toml_key_missing("tool.poetry")
    assert delfino.dockerhub, pyproject_toml_key_missing("tool.delfino.dockerhub")

    print_header("Running Docker build")

    flags: ArgsList = []

    poetry = app_context.py_project_toml.tool.poetry
    project_name = poetry.name
    project_version = poetry.version

    python_version = Version(poetry.dependencies["python"].strip("<>=~^"))
    flags.extend(["--build-arg", f"PYTHON_VERSION='{python_version.major}.{python_version.minor}'"])

    dockerhub = delfino.dockerhub
    flags.extend(["--platform", ",".join(dockerhub.build_for_platforms)])

    if push:
        dockerhub_password = getenv("DOCKERHUB_PERSONAL_ACCESS_TOKEN")
        if not dockerhub_password:
            click.secho("⚠ The 'DOCKERHUB_PERSONAL_ACCESS_TOKEN' environment variable is not set.", fg="yellow")
            dockerhub_password = getpass("Dockerhub Personal Access Token: ")
        run(f"docker login --username {dockerhub.username} --password {dockerhub_password}", on_error=OnError.EXIT)

        flags.extend(["--output", "type=image,push=true"])

    if getenv("CI"):  # https://circleci.com/docs/2.0/env-vars/#built-in-environment-variables
        flags.extend(["--progress", "plain"])

    _install_emulators(dockerhub.build_for_platforms)

    # While `docker buildx build` supports multiple `--tag` flags, push of them fails to expose
    # all architectures in `latest`. Multiple pushes fix this.
    for tag in [project_version, "latest"]:
        print_header(f"Build {dockerhub.username}/{project_name}:{tag}", level=2, icon="🔨")

        flags_for_tag = list(flags)
        if tag != "latest" and push:
            flags_for_tag.extend(["--cache-to", f"type=registry,ref={dockerhub.username}/{project_name}"])

        run(
            [
                "docker",
                "buildx",
                "build",
                "--cache-from",
                f"type=registry,ref={dockerhub.username}/{project_name}",
                "--tag",
                f"{dockerhub.username}/{project_name}:{tag}",
                *flags_for_tag,
                ".",
            ],
            on_error=OnError.EXIT,
        )

    if push:
        run("docker logout", on_error=OnError.EXIT)
