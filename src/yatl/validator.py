from requests import Response
from typing import Any, Callable
import json
from lxml import etree
from .utils import get_nested_value, get_content_type
from enum import StrEnum


class BodyFormat(StrEnum):
    """Enum for supported body formats."""

    JSON = "json"
    XML = "xml"
    TEXT = "text"

    @classmethod
    def from_content_type(cls, content_type: str) -> "BodyFormat":
        """Determines the body format from the content type.

        Args:
            content_type: The content type string.

        Returns:
            The corresponding BodyFormat enum value.
        """
        if content_type == "application/json":
            return cls.JSON
        elif content_type == "application/xml":
            return cls.XML
        elif content_type == "text/plain":
            return cls.TEXT
        else:
            raise ValueError(f"Unsupported content type: {content_type}")


def validate_json_body(response: Response, expected_json: dict[str, Any]) -> None:
    """Validates that the JSON response matches the expected structure.

    Args:
        response: The HTTP response containing JSON data.
        expected_json: A dictionary of expected key-value pairs.
            Nested dictionaries are validated recursively.

    Raises:
        AssertionError: If the response is not valid JSON, or any key
            is missing, or any value differs.
    """
    try:
        data = response.json()
    except json.JSONDecodeError:
        raise AssertionError("Response is not valid JSON")
    _validate_json_response(data, expected_json)


def _validate_json_response(
    data: dict[str, Any], expected_json: dict[str, Any]
) -> None:
    """Recursively validates a JSON object against an expected dictionary.

    Supports dot-notation keys for validating deep nested fields.

    Args:
        data: The actual JSON dictionary (or sub-dictionary).
        expected_json: The expected dictionary for this level.

    Raises:
        AssertionError: If a key is missing or a value mismatches.
    """
    for key, expected_value in expected_json.items():
        if "." in key:
            try:
                actual = get_nested_value(data, key)
            except ValueError as e:
                raise AssertionError(f"Path '{key}' not found in response: {e}")
            if actual != expected_value:
                raise AssertionError(
                    f"For path '{key}' expected '{expected_value}', got '{actual}'"
                )
        else:
            # Plain key
            if key not in data:
                raise AssertionError(f"Key '{key}' is missing in response")
            actual = data[key]
            if isinstance(actual, dict) and isinstance(expected_value, dict):
                _validate_json_response(actual, expected_value)
            elif actual != expected_value:
                raise AssertionError(
                    f"For key '{key}' expected '{expected_value}', got '{actual}'"
                )


def validate_xml_body(response: Response, expected_xml: dict[str, Any]) -> None:
    """Validates that the XML response contains elements with expected text.

    Args:
        response: The HTTP response containing XML data.
        expected_xml: A dictionary mapping XPath expressions to expected
            text values.

    Raises:
        AssertionError: If the response is not valid XML, an XPath matches
            no elements, or the text of the first matching element differs.
    """
    try:
        root = etree.fromstring(response.content)
    except etree.XMLSyntaxError:
        raise AssertionError("Response is not valid XML")
    for xpath, expected_value in expected_xml.items():
        elements = root.xpath(xpath)
        if not elements:
            raise AssertionError(f"XML element with xpath '{xpath}' not found")
        actual = elements[0].text
        if actual != expected_value:
            raise AssertionError(
                f"XML element '{xpath}' expected '{expected_value}', got '{actual}'"
            )


def validate_text_body(response: Response, expected_text: str) -> None:
    """Validates that the plain-text response contains a given substring.

    Args:
        response: The HTTP response with text content.
        expected_text: The substring that must appear in the response body.

    Raises:
        AssertionError: If the substring is not found.
    """
    actual_text = response.text
    if expected_text not in actual_text:
        raise AssertionError(f"Expected text '{expected_text}' not found in response")


class ResponseValidator:
    """Validates an HTTP response against a set of expectations.

    Expectations can include status code, headers, and body content (JSON, XML,
    or plain text). Validation failures raise `AssertionError` with descriptive
    messages.
    """

    _body_validators = {
        BodyFormat.JSON: validate_json_body,
        BodyFormat.XML: validate_xml_body,
        BodyFormat.TEXT: validate_text_body,
    }

    def __init__(self, response: Response, expect_spec: dict[str, Any]):
        """Initializes the validator with a response and expectation spec.

        Args:
            response: The HTTP response to validate.
            expect_spec: A dictionary containing expectations (status, headers, body).
        """
        self.response = response
        self.expect_spec = expect_spec

    def _validate_status(self) -> None:
        """Validates that the response status code matches the expected one.

        Raises:
            AssertionError: If the status code does not match.
        """
        expected_status = self.expect_spec.get("status")
        if expected_status is not None and self.response.status_code != expected_status:
            raise AssertionError(
                f"Expected status {expected_status}, got {self.response.status_code}"
            )

    def _normalize_header_value(self, key: str, value: str) -> str:
        """Normalizes a header value for comparison.

        For the Content-Type header, removes parameters (e.g., charset).
        For other headers, returns the value unchanged.

        Args:
            key: Header name.
            value: Header value.

        Returns:
            Normalized value.
        """
        if key.lower() == "content-type":
            # Strip parameters like charset
            return value.split(";")[0].strip().lower()
        return value

    def _validate_headers(self) -> None:
        """Validates that all expected headers are present and match.

        Raises:
            AssertionError: If a header is missing or its normalized value
                does not match the expected one.
        """
        expected_headers = self.expect_spec.get("headers")
        if expected_headers:
            for key, expected_value in expected_headers.items():
                actual = self.response.headers.get(key)
                if actual is None:
                    raise AssertionError(f"Header '{key}' is missing")
                norm_expected = self._normalize_header_value(key, expected_value)
                norm_actual = self._normalize_header_value(key, actual)
                if norm_actual != norm_expected:
                    raise AssertionError(
                        f"Header '{key}' expected '{norm_expected}', got '{norm_actual}' (original: '{actual}')"
                    )

    def _get_body_validator(self, content_type: str) -> Callable | None:
        """Return appropriate body validator based on content-type.

        Args:
            content_type: The content-type string.

        Returns:
            A validator function or None if no match.
        """
        try:
            fmt = BodyFormat.from_content_type(content_type)
            return self._body_validators.get(fmt)
        except ValueError:
            return None

    def check_expectations(self) -> None:
        """Runs all validations defined in the expectation spec.

        Validates status, headers, and body (based on content-type). The body
        validation is dispatched to the appropriate validator (JSON, XML, or text).

        Raises:
            AssertionError: If any validation fails.
        """
        self._validate_status()
        self._validate_headers()

        body_spec = self.expect_spec.get("body")
        if body_spec is None:
            return

        content_type = get_content_type(response=self.response)
        validator = self._get_body_validator(content_type)

        if validator is not None:
            if isinstance(body_spec, dict) and BodyFormat.JSON in body_spec:
                validator(self.response, body_spec[BodyFormat.JSON])
            elif isinstance(body_spec, dict) and BodyFormat.XML in body_spec:
                validator(self.response, body_spec[BodyFormat.XML])
            elif isinstance(body_spec, dict) and BodyFormat.TEXT in body_spec:
                validator(self.response, body_spec[BodyFormat.TEXT])
            else:
                if content_type == "application/json":
                    validate_json_body(self.response, body_spec)
                elif content_type == "application/xml":
                    validate_xml_body(self.response, body_spec)
                elif content_type == "text/plain":
                    validate_text_body(self.response, body_spec)
                else:
                    raise AssertionError(
                        f"Unsupported body validation for content-type: {content_type}"
                    )
        else:
            if isinstance(body_spec, dict) and BodyFormat.JSON in body_spec:
                validate_json_body(self.response, body_spec[BodyFormat.JSON])
            elif isinstance(body_spec, dict) and BodyFormat.TEXT in body_spec:
                validate_text_body(self.response, body_spec[BodyFormat.TEXT])
            else:
                raise AssertionError(
                    f"Unsupported body validation for content-type: {content_type}"
                )
