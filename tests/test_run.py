from src.yatl.utils import create_context, load_test_yaml, search_files
from src.yatl.run import is_skipped
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
def test_is_skipped(expected):
    """Проверяет, что is_skipped возвращает значение ключа 'skip' (по умолчанию False)."""
    item = {"skip": expected}
    assert is_skipped(item) is expected


def test_load_test_yaml():
    "Test that load_test_yaml returns a dictionary with test data."
    data = load_test_yaml("tests/data/ping.yatl.yaml")
    assert data is not None
    assert len(data) > 0


def test_load_test_yaml_with_invalid_file():
    "Test that load_test_yaml returns None with invalid file."
    with pytest.raises(FileNotFoundError):
        load_test_yaml("tests/data/not_found.yatl.yaml.invalid")


def test_search_files():
    "Test that search_files returns a list of files."
    files = search_files("tests/data")
    assert len(files) == 2


def test_search_files_with_invalid_path():
    "Test that search_files returns an empty list with invalid path."
    files = search_files("tests/data/not_found")
    assert len(files) == 0
