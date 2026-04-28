from typing import Protocol, Any
from jinja2 import Template


class ITemplateRenderer(Protocol):
    "Protocol for template renderers."

    def _get_template(self, template_str: str) -> Template: ...

    def render_data(self, data: Any, context: dict[str, Any]) -> Any: ...


class IReporter(Protocol):
    "Protocol for reporters."

    def add_info(self, message: str) -> None: ...

    def print_info(self) -> None: ...


class IResponseValidator(Protocol):
    """Protocol for response validators."""

    def check_expectations(self) -> None:
        """Validates the response against expectations.

        Raises:
            AssertionError: If any validation fails.
        """
        ...
