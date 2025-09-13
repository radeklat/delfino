import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import pytest
import toml

from delfino.config import ConfigValidationError, load_config
from delfino.models import Delfino, PyprojectToml, Tool


@contextmanager
def mock_rc_files(configs: list[Delfino | dict]) -> Iterator[list[Path]]:
    rc_files = []

    try:
        for config in configs:
            file = Path(tempfile.NamedTemporaryFile().name)
            if isinstance(config, Delfino):
                content = PyprojectToml(tool=Tool(delfino=config)).model_dump(exclude_defaults=True, exclude_unset=True)
            else:
                content = config
            file.write_text(toml.dumps(content), encoding="utf-8")
            rc_files.append(file)

        with patch("delfino.config._rc_locations", return_value=rc_files):
            yield rc_files
    finally:
        for rc_file in rc_files:
            try:
                rc_file.unlink()
            except FileNotFoundError:
                pass


class TestLoadConfig:
    @staticmethod
    def test_should_return_empty_config_when_no_files_are_found():
        rc_files = []
        for _ in range(3):
            with tempfile.NamedTemporaryFile(delete=True) as file:
                rc_files.append(Path(file.name))

        with patch("delfino.config._rc_locations", return_value=rc_files):
            config = load_config(Path())

        assert isinstance(config, PyprojectToml)
        assert config.model_dump(exclude_defaults=True, exclude_unset=True) == {}

    @staticmethod
    def test_should_choose_last_available_config():
        configs: list[Delfino | dict] = [
            Delfino(command_groups={"1": ["last"]}),
            Delfino(command_groups={"1": ["middle"]}),
            Delfino(command_groups={"1": ["first"]}),
        ]
        with mock_rc_files(configs):
            config = load_config(Path())

        assert isinstance(config, PyprojectToml)
        assert config.model_dump(exclude_defaults=True, exclude_unset=True) == {
            "tool": {"delfino": {"command_groups": {"1": ["first"]}}}
        }

    @staticmethod
    def test_should_raise_validation_error_from_the_first_invalid_config():
        configs: list[Delfino | dict] = [
            Delfino(command_groups={"1": ["valid"]}),
            {"tool": {"delfino": {"command_groups": {"2": "invalid"}}}},
            Delfino(command_groups={"3": ["also_valid"]}),
        ]
        with mock_rc_files(configs) as rc_files:
            expected_exc_msg = f"Delfino appears to be misconfigured in '{rc_files[1]}'.*"

            with pytest.raises(ConfigValidationError, match=expected_exc_msg):
                load_config(Path())
