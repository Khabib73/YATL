from src.yatl.run import Runner
from src.yatl.extractor import DataExtractor
from src.yatl.render import TemplateRenderer


def test_create_context_with_valid_data_returns_context():
    data = {
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
    run = Runner(DataExtractor(), TemplateRenderer())
    context = run.create_context(data)
    assert context is not None
    assert context["base_url"] == "https://yandex.ru"
    assert context["name"] == "ping"


def test_create_context_with_empty_data_returns_empty_context():
    run = Runner(DataExtractor(), TemplateRenderer())
    context = run.create_context({})
    assert len(context) == 0
