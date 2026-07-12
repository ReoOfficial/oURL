import pytest

from cli.validator import (
    validate_url,
    validate_method,
    validate_headers,
    validate_timeout,
    validate_auth,
    validate_forms,
)

from utils.errors import (
    InvalidURLException,
    InvalidMethodException,
    InvalidHeaderException,
    InvalidTimeoutException,
    InvalidAuthException,
    InvalidFormException,
)


def test_valid_url():
    assert validate_url("https://example.com") is None


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
    assert validate_method("GET") is None


def test_lowercase_method():
    assert validate_method("post") is None


def test_no_custom_method():
    assert validate_method(None) is None


def test_invalid_method():
    with pytest.raises(InvalidMethodException):
        validate_method("WRONG")


def test_valid_header():
    assert validate_headers(
        ["Accept: application/json"]
    ) is None


def test_multiple_headers():
    assert validate_headers(
        [
            "Accept: application/json",
            "User-Agent: MyCurl/2.0",
        ]
    ) is None


def test_header_without_colon():
    with pytest.raises(InvalidHeaderException):
        validate_headers(["WrongHeader"])


def test_header_with_empty_name():
    with pytest.raises(InvalidHeaderException):
        validate_headers([": value"])


def test_valid_timeout():
    assert validate_timeout(15) is None


@pytest.mark.parametrize("timeout", [0, -1, -100])
def test_invalid_timeout(timeout):
    with pytest.raises(InvalidTimeoutException):
        validate_timeout(timeout)

def test_valid_decimal_timeout():
    assert validate_timeout(5.5) is None

def test_valid_auth():
    assert validate_auth("user:password") is None


def test_invalid_auth_without_colon():
    with pytest.raises(InvalidAuthException):
        validate_auth("no_password")


def test_auth_with_empty_username():
    with pytest.raises(InvalidAuthException):
        validate_auth(":password")


def test_valid_form():
    assert validate_forms(["name=Reo"]) is None


def test_invalid_form_without_equals():
    with pytest.raises(InvalidFormException):
        validate_forms(["name"])


def test_form_with_empty_name():
    with pytest.raises(InvalidFormException):
        validate_forms(["=Reo"])