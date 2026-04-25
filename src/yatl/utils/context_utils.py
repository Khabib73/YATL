from itertools import takewhile
from typing import Any


def create_context(test_spec: dict) -> dict[str, Any]:
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
