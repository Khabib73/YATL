import pytest
from src.yatl.extractor import DataExtractor
from src.yatl.render import TemplateRenderer
from src.yatl.step_executor import StepExecutor
from src.yatl.run import Runner, Reporter, SkipChecker, TestLoader


@pytest.fixture
def data_extractor():
    return DataExtractor()


@pytest.fixture
def template_render():
    return TemplateRenderer()


@pytest.fixture
def step_executor(data_extractor, template_render):
    return StepExecutor(data_extractor, template_render)


@pytest.fixture
def reporter():
    return Reporter()


@pytest.fixture
def skip_checker():
    return SkipChecker()


@pytest.fixture
def test_loader():
    return TestLoader()


@pytest.fixture
def runner(step_executor, reporter, skip_checker, test_loader):
    return Runner(step_executor, reporter, skip_checker, test_loader)


@pytest.fixture
def data():
    return {
        "base_url": "https://yandex.ru",
        "name": "ping",
        "steps": [
            {
                "expect": {"status": 200},
                "name": "ok_test",
                "request": {"method": "GET"},
            },
            {
                "expect": {"status": 404},
                "name": "not_found_test",
                "request": {"method": "GET", "url": "/not_found"},
            },
        ],
    }
