from getpass import getpass
from os import getenv
from pathlib import Path
from typing import List

import click

from delfino.constants import PackageManager
from delfino.contexts import AppContext, pass_app_context
from delfino.execution import OnError, run
from delfino.models.pyproject_toml import Dockerhub
from delfino.terminal_output import print_header
from delfino.utils import ArgsList
from delfino.validation import assert_package_manager_is_known, assert_pip_package_installed, pyproject_toml_key_missing

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


def _docker_build(
    project_name: str,
    dockerhub: Dockerhub,
    flags: ArgsList,
    platform: str,
    tag: str = "latest",
    push: bool = False,
):
    _flags = list(flags)
    _flags.extend(["--platform", platform])
    if tag != "latest" and push:
        _flags.extend(["--cache-to", f"type=registry,ref={dockerhub.username}/{project_name}"])

    run(
        [
            "docker",
            "buildx",
            "build",
            "--cache-from",
            f"type=registry,ref={dockerhub.username}/{project_name}",
            "--tag",
            f"{dockerhub.username}/{project_name}:{tag}",
            *_flags,
            ".",
        ],
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
@click.option("--serialized", is_flag=True, help="Do not build multiple platforms concurrently.")
@pass_app_context
def build_docker(app_context: AppContext, push: bool, serialized: bool):
    """Build and push a docker image."""
    delfino = app_context.pyproject_toml.tool.delfino
    dockerfile = Path("Dockerfile")

    assert_package_manager_is_known(app_context.package_manager)
    assert (
        app_context.package_manager == PackageManager.POETRY
    ), f"Only the '{PackageManager.POETRY.value}' package manager is supported by this command."
    assert_pip_package_installed("packaging")
    assert dockerfile.exists() and dockerfile.is_file(), "File 'Dockerfile' not found but required by this command."
    assert app_context.pyproject_toml.tool.poetry, pyproject_toml_key_missing("tool.poetry")
    assert delfino.dockerhub, pyproject_toml_key_missing("tool.delfino.dockerhub")

    print_header("Running Docker build")

    flags: ArgsList = []

    poetry = app_context.pyproject_toml.tool.poetry
    project_name = poetry.name
    project_version = poetry.version

    python_version = Version(poetry.dependencies["python"].strip("<>=~^"))
    flags.extend(["--build-arg", f"PYTHON_VERSION={python_version.major}.{python_version.minor}"])

    dockerhub = delfino.dockerhub

    if push:
        dockerhub_password = getenv("DOCKERHUB_PERSONAL_ACCESS_TOKEN")
        if not dockerhub_password:
            click.secho("⚠ The 'DOCKERHUB_PERSONAL_ACCESS_TOKEN' environment variable is not set.", fg="yellow")
            dockerhub_password = getpass("Dockerhub Personal Access Token: ")
        run(f"docker login --username {dockerhub.username} --password {dockerhub_password}", on_error=OnError.EXIT)

    if getenv("CI"):  # https://circleci.com/docs/2.0/env-vars/#built-in-environment-variables
        flags.extend(["--progress", "plain"])

    joined_build_platforms = ",".join(dockerhub.build_for_platforms)
    if serialized:
        build_platforms: List[str] = dockerhub.build_for_platforms
    else:
        build_platforms = [joined_build_platforms]
        _install_emulators(dockerhub.build_for_platforms)

    # If serialized build is selected, run build individually. Results are cached so the second
    # build below will only push and not build again.
    for platform in build_platforms:
        if serialized:
            _install_emulators([platform])
        print_header(f"Build {dockerhub.username}/{project_name}:latest for {platform}", level=2, icon="🔨")
        _docker_build(project_name, dockerhub, flags, platform)

    if not push:
        return

    flags.extend(["--output", "type=image,push=true"])

    # While `docker buildx build` supports multiple `--tag` flags, push of them fails to expose
    # all architectures in `latest`. Multiple pushes fix this.
    for tag in [project_version, "latest"]:
        print_header(f"Push {dockerhub.username}/{project_name}:{tag}", level=2, icon="🔨")
        _docker_build(project_name, dockerhub, flags, joined_build_platforms, tag, push)

    run("docker logout", on_error=OnError.EXIT)
