from .extractor import DataExtractor
from .request_builder import send_request
from typing import Any, Callable
from .interface import ITemplateRenderer, IResponseValidator
from requests import Response


def execute_step(
    step: dict[str, Any],
    context: dict[str, Any],
    data_extractor: DataExtractor,
    template_renderer: ITemplateRenderer,
    response_validator: Callable[[Response, dict[str, Any]], IResponseValidator],
) -> dict[str, Any]:
    """Executes a single test step and returns the updated context.

    The step is first rendered with the current context, then the request
    is sent. If the step contains an `expect` block, the response is validated.
    If it contains an `extract` block, values are extracted and added to the
    context for subsequent steps.

    Args:
        step: The raw step dictionary (may contain templates).
        context: The current context (global variables).
        data_extractor: Used to extract values from responses.
        template_renderer: Used to render templates in the step.
        response_validator: Factory function that creates a validator instance
            from a response and expectation dictionary.

    Returns:
        The updated context (with newly extracted values, if any).
    """
    resolved_step = template_renderer.render_data(step, context)
    response = send_request(context, resolved_step)

    if "expect" in resolved_step:
        validator = response_validator(response, resolved_step["expect"])
        validator.check_expectations()

    if "extract" in resolved_step:
        extracted = data_extractor.extract(response, resolved_step["extract"])
        context.update(extracted)

    return context
