from typing import Any
from requests import request, Response


def send_request(context: dict[str, Any], resolved_step: dict[str, Any]) -> Response:
    """Builds and sends the HTTP request described by the step.

    Args:
        context: The current context (contains base_url, previous extracts, etc.)
        resolved_step: The step dictionary after template rendering.

    Returns:
        The HTTP response object.
    """
    request_data = build_request_data(context, resolved_step)
    response = request(**request_data)
    return response


def build_request_data(
    context: dict[str, Any], resolved_step: dict[str, Any]
) -> dict[str, Any]:
    """Produces the keyword arguments for `requests.request`.

    Extracts method, URL, headers, parameters, cookies, timeout, and body
    from the step's `request` block. Automatically sets Content-Type headers
    based on the body format (JSON, XML, text, form-data, files).

    Returns:
        A dictionary that can be unpacked as `requests.request(**kwargs)`.

    Raises:
        ValueError: If the body has an unsupported type.
    """
    request_data: dict[str, Any] = resolved_step["request"]
    method, url, timeout, headers, params, cookies, body = extract_request_params(
        request_data
    )

    url = build_url(context.get("base_url", ""), url)

    kwargs: dict[str, Any] = {
        "method": method,
        "url": url,
        "timeout": timeout,
        "headers": headers,
        "params": params,
        "cookies": cookies,
    }

    if body is not None:
        process_body(body, headers, kwargs)

    kwargs["headers"] = headers
    return kwargs


def build_url(base_url: str, url: str) -> str:
    """Constructs a full URL by prepending the base URL from context.

    Args:
        base_url: The base URL from context (may be empty).
        url: The relative or absolute URL from the step.

    Returns:
        The absolute URL. If the context contains a `base_url`, it is
        prepended (with proper slash handling). If `url` is already absolute,
        the base URL is ignored (but currently not implemented).
    """
    if not base_url.startswith("http"):
        base_url = "https://" + base_url
    if url.startswith("http"):
        url = url.lstrip("https://")
    return base_url.rstrip("/") + "/" + url.lstrip("/")


def extract_request_params(
    request_data: dict[str, Any],
) -> tuple[str, str, Any, dict, dict, dict, Any]:
    """Extracts request parameters from the request data dictionary.

    Returns:
        Tuple of (method, url, timeout, headers, params, cookies, body)
    """
    method = str(request_data.get("method", "GET")).upper()
    url: str = request_data.get("url", "")
    timeout = request_data.get("timeout", None)
    headers = request_data.get("headers", {})
    body: dict[str, Any] | str | None = request_data.get("body", None)
    params = request_data.get("params", {})
    cookies = request_data.get("cookies", {})

    return method, url, timeout, headers, params, cookies, body


def process_body(
    body: dict[str, Any] | str, headers: dict[str, str], kwargs: dict[str, Any]
) -> None:
    """Processes the request body and updates kwargs and headers accordingly.

    Args:
        body: The body from the request data.
        headers: The headers dictionary (may be modified).
        kwargs: The kwargs dictionary for requests.request (may be modified).

    Raises:
        ValueError: If the body has an unsupported type.
    """
    if isinstance(body, dict):
        if "json" in body:
            kwargs["json"] = body["json"]
            _set_content_type(headers, "application/json")
        elif "xml" in body:
            xml_content = body["xml"]
            if isinstance(xml_content, str):
                kwargs["data"] = xml_content
                _set_content_type(headers, "application/xml")
        elif "text" in body:
            kwargs["data"] = body["text"]
            _set_content_type(headers, "text/plain")
        elif "form" in body:
            kwargs["data"] = body["form"]
            _set_content_type(headers, "application/x-www-form-urlencoded")
        elif "files" in body:
            kwargs["files"] = body["files"]
        else:
            kwargs["json"] = body
    elif isinstance(body, str):
        kwargs["data"] = body
        _set_content_type(headers, "text/plain")
    else:
        raise ValueError(f"Unsupported body type: {type(body)}")


def _set_content_type(headers: dict[str, str], content_type: str) -> None:
    """Sets the Content-Type header if not already present.

    Args:
        headers: The headers dictionary (modified in place).
        content_type: The content type to set.
    """
    if "Content-Type" not in headers:
        headers["Content-Type"] = content_type


class RequestBuilder:
    """Legacy class for building request arguments.

    Deprecated: Use the module-level functions instead.
    """

    def __init__(self, context: dict[str, Any], resolved_step: dict[str, Any]):
        self.context = context
        self.resolved_step = resolved_step

    def send_request(self) -> Response:
        """Builds and sends the HTTP request described by the step."""
        return send_request(self.context, self.resolved_step)

    def build_request_data(self) -> dict[str, Any]:
        """Produces the keyword arguments for `requests.request`."""
        return build_request_data(self.context, self.resolved_step)

    def build_url(self, url: str) -> str:
        """Constructs a full URL by prepending the base URL from context."""
        return build_url(self.context.get("base_url", ""), url)
