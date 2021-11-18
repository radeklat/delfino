from tests.constants import PROJECT_VERSION


class TestProject:
    @staticmethod
    def should_have_a_version():
        assert PROJECT_VERSION
