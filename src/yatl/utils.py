from itertools import takewhile
import os
from typing import Any
from requests import Response


def create_context(test_spec: dict):
    """Creates the initial context from the test specification.

    The context consists of all top-level keys that appear before the
    "steps" key in the YAML document. This typically includes `base_url`,
    `name`, `description`, and any user-defined variables.

    Args:
        test_spec: The parsed YAML dictionary.

    Returns:
        A dictionary containing the initial context.
    """
    return {k: v for k, v in takewhile(lambda x: x[0] != "steps", test_spec.items())}


def search_files(base_path: str) -> list[str]:
    """Recursively searches for test files with a .test.yaml/.test.yml suffix.

    Args:
        base_path: Base directory for the search.

    Returns:
        List of found file paths.
    """
    files = []

    def _search(current_path: str):
        try:
            os.listdir(current_path)
        except FileNotFoundError:
            return
        for item in os.listdir(current_path):
            full_path = os.path.join(current_path, item)
            if os.path.isfile(full_path) and (
                item.endswith(".test.yaml") or item.endswith(".test.yml")
            ):
                files.append(full_path)
            elif os.path.isdir(full_path):
                _search(full_path)

    _search(base_path)
    return files


def get_content_type(response: Response) -> str:
    """Extracts the media type from the response's Content-Type header.

    Returns:
        The media type without parameters, lowercased.
        If the header is missing, returns an empty string.
    """
    ct = response.headers.get("content-type", "")
    return ct.split(";")[0].strip().lower()


def get_nested_value(data: Any, path: str) -> Any:
    """Retrieve a value from a nested dict using dot notation.

    Args:
        data: A dictionary (or list) containing the data.
        path: A dot-separated string representing the path (e.g., "user.email").

    Returns:
        The value at the given path.

    Raises:
        ValueError: If any component of the path does not exist.
    """
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and key.isdigit() and int(key) < len(current):
            current = current[int(key)]
        elif isinstance(current, list):
            raise ValueError(f"Path component '{key}' is not an index in {current}")
        else:
            raise ValueError(f"Path component '{key}' not found in {current}")
    return current
