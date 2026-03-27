from src.yatl.utils import create_context
import pytest


def test_create_context_with_valid_data_returns_context(data):
    "Test that create_context returns a context with valid data."
    context = create_context(data)
    assert context is not None
    assert context["base_url"] == "https://yandex.ru"
    assert context["name"] == "ping"


def test_create_context_with_empty_data_returns_empty_context():
    "Test that create_context returns an empty context with empty data."
    context = create_context({})
    assert len(context) == 0


@pytest.mark.parametrize("expected", [True, False])
def test_is_skipped_test(expected, skip_checker):
    "Test that is_skipped_test returns True if test is skipped."
    data = {"skip": expected}
    assert skip_checker.is_skipped_test(data) is expected
