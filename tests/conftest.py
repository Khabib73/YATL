import pytest
from src.yatl.extractor import DataExtractor
from src.yatl.render import TemplateRenderer
from src.yatl.validator import ResponseValidator
from src.yatl.run import Runner


@pytest.fixture
def data_extractor():
    return DataExtractor()


@pytest.fixture
def template_render():
    return TemplateRenderer()


@pytest.fixture
def runner(data_extractor, template_render):
    return Runner(data_extractor, template_render, ResponseValidator)


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
