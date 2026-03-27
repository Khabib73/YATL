from itertools import takewhile
import yaml
import os
from requests import Response
from typing import Any


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


def load_yaml_test(path_file: str):
    """Loads and parses a YAML test file.

    Args:
        yaml_path: Path to the .test.yaml or .test.yml file.

    Returns:
        The parsed YAML as a dictionary, or None if the file is empty.
    """
    with open(path_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def search_files(current_path: str, item: str, files: list):
    """Recursively searches for test files with a .test.yaml/.test.yml suffix.

    Args:
        current_path: Base directory for the search.
        item: Current file or directory name relative to `current_path`.
        files: Accumulator list where found file paths are appended.

    Returns:
        The same `files` list (modified in-place).
    """
    full_path = os.path.join(current_path, item)
    if os.path.isfile(full_path) and (
        item.endswith(".test.yaml") or item.endswith(".test.yml")
    ):
        files.append(full_path)
        return
    elif os.path.isdir(full_path):
        for dir in os.listdir(full_path):
            search_files(full_path, dir, files)
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
        else:
            raise ValueError(f"Path component '{key}' not found in {current}")
    return current
