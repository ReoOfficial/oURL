import pytest

from utils.helpers import (
    parse_headers,
    parse_auth,
    parse_cookies,
    parse_forms,
)


def test_parse_single_header():
    result = parse_headers(["Accept: application/json"])

    assert result == {
        "Accept": "application/json"
    }


def test_parse_multiple_headers():
    result = parse_headers([
        "Accept: application/json",
        "User-Agent: MyCurl/2.0",
    ])

    assert result == {
        "Accept": "application/json",
        "User-Agent": "MyCurl/2.0",
    }


def test_header_value_can_contain_colon():
    result = parse_headers([
        "Authorization: Bearer abc:def"
    ])

    assert result == {
        "Authorization": "Bearer abc:def"
    }


def test_parse_auth():
    result = parse_auth("Reo:secret")

    assert result == ("Reo", "secret")


def test_auth_password_can_contain_colon():
    result = parse_auth("Reo:secret:password")

    assert result == ("Reo", "secret:password")


def test_parse_no_auth():
    assert parse_auth(None) is None


def test_parse_single_cookie():
    result = parse_cookies("session=abc123")

    assert result == {
        "session": "abc123"
    }


def test_parse_multiple_cookies():
    result = parse_cookies(
        "session=abc123; theme=dark"
    )

    assert result == {
        "session": "abc123",
        "theme": "dark",
    }


def test_parse_no_cookies():
    assert parse_cookies(None) == {}


def test_parse_form_data():
    data, files = parse_forms([
        "name=Reo",
        "role=developer",
    ])

    assert data == {
        "name": "Reo",
        "role": "developer",
    }

    assert files == {}