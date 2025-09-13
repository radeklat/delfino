import sys
import tempfile
from pathlib import Path
from typing import Any

import click
import pytest

from delfino.decorators import files_folders_option, pass_args
from delfino.models.pyproject_toml import PluginConfig
from tests.integration.assertions import assert_output_matches


class CustomPluginConfig(PluginConfig):
    cmd: dict[str, Any]


@click.command("cmd")
@click.option("--option")
@pass_args
def _command(option, passed_args):
    print((option,) + passed_args)


@click.command()
@files_folders_option
@pass_args
def _command_with_filepaths_argument_first(files_folders, passed_args):
    print(files_folders + passed_args)


@click.command()
@pass_args
@files_folders_option
def _command_with_filepaths_argument_second(files_folders, passed_args):
    print(files_folders + passed_args)


class TestPassArgsDecorator:
    @staticmethod
    def test_should_pass_arguments_from_command_line(runner, context_obj):
        result = runner.invoke(_command, "-- --option 1 argument", obj=context_obj)
        assert_output_matches(result, None, "--option", "1", "argument")

    @staticmethod
    def test_should_pass_arguments_from_config(runner, context_obj):
        context_obj.plugin_config = CustomPluginConfig(cmd={"pass_args": "--option 1 argument"})
        result = runner.invoke(_command, obj=context_obj)
        assert_output_matches(result, None, "--option", "1", "argument")

    @staticmethod
    def test_should_prefer_command_line_arguments_over_config(runner, context_obj):
        context_obj.plugin_config = CustomPluginConfig(cmd={"pass_args": "config"})
        result = runner.invoke(_command, "-- commandline", obj=context_obj)
        assert_output_matches(result, None, "commandline")

    @staticmethod
    def test_should_not_override_command_options_of_the_same_name_from_config(runner, context_obj):
        context_obj.plugin_config = CustomPluginConfig(cmd={"pass_args": "--option passed"})
        result = runner.invoke(_command, "--option option", obj=context_obj)
        assert_output_matches(result, "option", "--option", "passed")

    @staticmethod
    def test_should_not_override_command_options_of_the_same_name_from_command_line(runner, context_obj):
        result = runner.invoke(_command, "--option option -- --option passed", obj=context_obj)
        assert_output_matches(result, "option", "--option", "passed")

    @staticmethod
    def test_should_allow_empty_config(runner, context_obj):
        context_obj.plugin_config = CustomPluginConfig(cmd={"pass_args": ""})
        result = runner.invoke(_command, obj=context_obj)
        assert_output_matches(result, None)

    @staticmethod
    def test_should_allow_empty_command_line_pass_args(runner, context_obj):
        result = runner.invoke(_command, "--", obj=context_obj)
        assert_output_matches(result, None)

    @staticmethod
    @pytest.mark.parametrize(
        "command",
        [
            pytest.param(_command_with_filepaths_argument_second, id="after this decorator"),
            pytest.param(_command_with_filepaths_argument_first, id="before this decorator"),
        ],
    )
    def test_should_not_conflict_with_filepaths_argument(runner, context_obj, command):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            file1 = tmpdir_path / "file1.py"
            file1.touch()
            folder = tmpdir_path / "folder"
            folder.mkdir()

            try:
                sys.path.append(tmpdir)
                result = runner.invoke(
                    command,
                    f"--file {file1} --folder {folder} -- --option 1 arg",
                    obj=context_obj,
                )
            finally:
                sys.path.pop()

        assert_output_matches(result, str(file1), str(folder), "--option", "1", "arg")
