from typing import Any, Dict, Union, Tuple
from requests import request, Response


def send_request(context: Dict[str, Any], resolved_step: Dict[str, Any]) -> Response:
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
    context: Dict[str, Any], resolved_step: Dict[str, Any]
) -> Dict[str, Any]:
    """Produces the keyword arguments for `requests.request`.

    Extracts method, URL, headers, parameters, cookies, timeout, and body
    from the step's `request` block. Automatically sets Content‑Type headers
    based on the body format (JSON, XML, text, form‑data, files).

    Returns:
        A dictionary that can be unpacked as `requests.request(**kwargs)`.

    Raises:
        ValueError: If the body has an unsupported type.
    """
    request_data: Dict[str, Any] = resolved_step["request"]
    method, url, timeout, headers, params, cookies, body = _extract_request_params(
        request_data
    )

    url = _build_url(context.get("base_url", ""), url)

    kwargs: Dict[str, Any] = {
        "method": method,
        "url": url,
        "timeout": timeout,
        "headers": headers,
        "params": params,
        "cookies": cookies,
    }

    if body is not None:
        _process_body(body, headers, kwargs)

    kwargs["headers"] = headers
    return kwargs


def _build_url(base_url: str, url: str) -> str:
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
    return base_url.rstrip("/") + "/" + url.lstrip("/")


def _extract_request_params(
    request_data: Dict[str, Any],
) -> Tuple[str, str, Any, Dict, Dict, Dict, Any]:
    """Extracts request parameters from the request data dictionary.

    Returns:
        Tuple of (method, url, timeout, headers, params, cookies, body)
    """
    method = str(request_data.get("method", "GET")).upper()
    url: str = request_data.get("url", "")
    timeout = request_data.get("timeout", None)
    headers = request_data.get("headers", {})
    body: Union[Dict[str, Any], str, None] = request_data.get("body")
    params = request_data.get("params", {})
    cookies = request_data.get("cookies", {})

    return method, url, timeout, headers, params, cookies, body


def _process_body(
    body: Union[Dict[str, Any], str], headers: Dict[str, str], kwargs: Dict[str, Any]
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


def _set_content_type(headers: Dict[str, str], content_type: str) -> None:
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

    def __init__(self, context: Dict[str, Any], resolved_step: Dict[str, Any]):
        self.context = context
        self.resolved_step = resolved_step

    def send_request(self) -> Response:
        """Builds and sends the HTTP request described by the step."""
        return send_request(self.context, self.resolved_step)

    def build_request_data(self) -> Dict[str, Any]:
        """Produces the keyword arguments for `requests.request`."""
        return build_request_data(self.context, self.resolved_step)

    def _build_url(self, url: str) -> str:
        """Constructs a full URL by prepending the base URL from context."""
        return _build_url(self.context.get("base_url", ""), url)
