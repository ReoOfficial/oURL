from types import SimpleNamespace

import pytest

from cli.validator import (
    validate,
    validate_auth,
    validate_forms,
    validate_headers,
    validate_method,
    validate_timeout,
    validate_url,
)
from utils.errors import (
    InvalidAuthException,
    InvalidFormException,
    InvalidHeaderException,
    InvalidMethodException,
    InvalidTimeoutException,
    InvalidURLException,
)


def test_valid_url():
    validate_url("https://example.com")


@pytest.mark.parametrize(
    "url",
    [
        "",
        "example.com",
        "not-a-url",
        "ftp://example.com",
    ],
)
def test_invalid_url(url):
    with pytest.raises(InvalidURLException):
        validate_url(url)


def test_valid_method():
    validate_method("GET")


def test_lowercase_method():
    validate_method("post")


def test_no_custom_method():
    validate_method(None)


def test_invalid_method():
    with pytest.raises(InvalidMethodException):
        validate_method("INVALID")


def test_valid_header():
    validate_headers(
        [
            "Content-Type: application/json",
        ]
    )


def test_multiple_headers():
    validate_headers(
        [
            "Content-Type: application/json",
            "Authorization: Bearer token",
        ]
    )


def test_header_without_colon():
    with pytest.raises(InvalidHeaderException):
        validate_headers(
            [
                "InvalidHeader",
            ]
        )


def test_header_with_empty_name():
    with pytest.raises(InvalidHeaderException):
        validate_headers(
            [
                ": empty-name",
            ]
        )


def test_valid_timeout():
    validate_timeout(10)


@pytest.mark.parametrize(
    "timeout",
    [
        0,
        -1,
        -100,
    ],
)
def test_invalid_timeout(timeout):
    with pytest.raises(InvalidTimeoutException):
        validate_timeout(timeout)


def test_valid_decimal_timeout():
    validate_timeout(5.5)


def test_valid_auth():
    validate_auth("user:password")


def test_invalid_auth_without_colon():
    with pytest.raises(InvalidAuthException):
        validate_auth("missing-password")


def test_auth_with_empty_username():
    with pytest.raises(InvalidAuthException):
        validate_auth(":password")


def test_validate_auth_with_no_auth():
    assert validate_auth(None) is None


def test_valid_form():
    validate_forms(
        [
            "name=Reo",
        ]
    )


def test_invalid_form_without_equals():
    with pytest.raises(InvalidFormException):
        validate_forms(
            [
                "missing-equals-sign",
            ]
        )


def test_form_with_empty_name():
    with pytest.raises(InvalidFormException):
        validate_forms(
            [
                "=value",
            ]
        )


def test_validate_runs_all_checks():
    args = SimpleNamespace(
        url="https://example.com",
        method="GET",
        header=[
            "Accept: application/json",
        ],
        max_time=5.5,
        user="reo:password",
        form=[
            "name=Reo",
        ],
    )

    result = validate(args)

    assert result is args