from click.testing import Result


def assert_output_matches(result: Result, *match):
    assert result.exit_code == 0, result.output
    assert result.stdout.rstrip() == str(tuple(match))
