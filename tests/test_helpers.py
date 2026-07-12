import pytest

from utils.helpers import save_cookies
from utils.errors import (
    FileWriteException,
    FileUploadException,
)

from unittest.mock import (
    mock_open,
    patch,
)
from utils.errors import InvalidCookieException

from utils.helpers import (
    parse_headers,
    parse_auth,
    parse_cookies,
    parse_forms,
)


def test_opened_files_are_closed_when_later_upload_fails():
    first_file = mock_open()
    first_handle = first_file.return_value

    def fake_open(filename, mode):
        if filename == "exists.txt":
            return first_handle

        raise FileNotFoundError(filename)

    with patch("builtins.open", side_effect=fake_open):
        with pytest.raises(FileUploadException):
            parse_forms([
                "first=@exists.txt",
                "second=@missing.txt",
            ])

    first_handle.close.assert_called_once()


def test_invalid_cookie_jar_path():
    with pytest.raises(FileWriteException):
        save_cookies(
            [],
            "folder_that_does_not_exist/cookies.txt",
        )

def test_malformed_cookie():
    with pytest.raises(InvalidCookieException):
        parse_cookies("malformed_cookie")


def test_cookie_with_empty_name():
    with pytest.raises(InvalidCookieException):
        parse_cookies("=abc123")


def test_parse_single_header():
    result = parse_headers(["Accept: application/json"])

    assert result == {
        "Accept": "application/json"
    }


def test_parse_multiple_headers():
    result = parse_headers([
        "Accept: application/json",
        "User-Agent: MyCurl/2.1",
    ])

    assert result == {
        "Accept": "application/json",
        "User-Agent": "MyCurl/2.1",
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