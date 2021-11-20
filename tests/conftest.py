from _pytest.fixtures import fixture
from click.testing import CliRunner


@fixture(scope="session")
def runner() -> CliRunner:
    return CliRunner()
