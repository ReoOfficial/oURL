import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import main as main_module

from utils.errors import (
    ConnectionException,
    FileUploadException,
    FileWriteException,
    InvalidAuthException,
    InvalidCookieException,
    InvalidFormException,
    InvalidHeaderException,
    InvalidMethodException,
    InvalidTimeoutException,
    InvalidURLException,
    RequestFailedException,
    RequestTimeoutException,
    TLSException,
    TooManyRedirectsException,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_FILE = PROJECT_ROOT / "main.py"


class FakeResponse:
    def get_cookies(self):
        return {
            "session": "abc123",
        }

    def get_content(self):
        return b"response bytes"


def make_args(**overrides):
    values = {
        "method": None,
        "data": None,
        "form": [],
        "url": "https://example.com",
        "header": [],
        "max_time": 15.0,
        "verbose": False,
        "location": False,
        "insecure": False,
        "user": None,
        "user_agent": None,
        "output": None,
        "head": False,
        "cookie": None,
        "cookie_jar": None,
    }

    values.update(overrides)

    return SimpleNamespace(**values)


def prepare_successful_main(monkeypatch, args):
    captured = {}

    response = FakeResponse()

    def fake_validate(received_args):
        captured["validated_args"] = received_args
        return received_args

    def fake_request(**kwargs):
        captured["request_kwargs"] = kwargs
        return SimpleNamespace(**kwargs)

    class FakeClient:
        def send(self, request):
            captured["sent_request"] = request
            return response

    def fake_format_response(request, received_response):
        captured["formatted_request"] = request
        captured["formatted_response"] = received_response
        return "formatted response"

    def fake_print_response(output, filename, content):
        captured["printed"] = {
            "output": output,
            "filename": filename,
            "content": content,
        }

    def fake_save_cookies(cookies, filename):
        captured["saved_cookies"] = {
            "cookies": cookies,
            "filename": filename,
        }

    monkeypatch.setattr(
        main_module,
        "parse_args",
        lambda: args,
    )

    monkeypatch.setattr(
        main_module,
        "validate",
        fake_validate,
    )

    monkeypatch.setattr(
        main_module,
        "parse_forms",
        lambda forms: (
            {"form-name": "form-value"},
            {},
        ),
    )

    monkeypatch.setattr(
        main_module,
        "parse_headers",
        lambda headers: {
            "X-Test": "hello",
        },
    )

    monkeypatch.setattr(
        main_module,
        "parse_auth",
        lambda auth: (
            "user",
            "password",
        )
        if auth
        else None,
    )

    monkeypatch.setattr(
        main_module,
        "parse_cookies",
        lambda cookies: {
            "theme": "dark",
        }
        if cookies
        else {},
    )

    monkeypatch.setattr(
        main_module,
        "Request",
        fake_request,
    )

    monkeypatch.setattr(
        main_module,
        "Client",
        FakeClient,
    )

    monkeypatch.setattr(
        main_module,
        "format_response",
        fake_format_response,
    )

    monkeypatch.setattr(
        main_module,
        "print_response",
        fake_print_response,
    )

    monkeypatch.setattr(
        main_module,
        "save_cookies",
        fake_save_cookies,
    )

    return captured


def test_main_uses_get_as_default_method(monkeypatch):
    args = make_args()

    captured = prepare_successful_main(
        monkeypatch,
        args,
    )

    main_module.main()

    assert args.method == "GET"
    assert captured["validated_args"] is args

    assert captured["request_kwargs"]["method"] == "GET"
    assert captured["request_kwargs"]["url"] == (
        "https://example.com"
    )

    assert captured["request_kwargs"]["headers"] == {
        "X-Test": "hello",
    }

    assert captured["request_kwargs"]["timeout"] == 15.0
    assert captured["request_kwargs"]["form_data"] == {
        "form-name": "form-value",
    }

    assert captured["printed"] == {
        "output": "formatted response",
        "filename": None,
        "content": b"response bytes",
    }

    assert "saved_cookies" not in captured


def test_main_uses_post_and_saves_cookies(monkeypatch):
    args = make_args(
        data="name=Reo",
        user="user:password",
        cookie="theme=dark",
        cookie_jar="cookies.txt",
        output="response.bin",
    )

    captured = prepare_successful_main(
        monkeypatch,
        args,
    )

    main_module.main()

    assert args.method == "POST"

    assert captured["request_kwargs"]["method"] == "POST"
    assert captured["request_kwargs"]["body"] == "name=Reo"

    assert captured["request_kwargs"]["auth"] == (
        "user",
        "password",
    )

    assert captured["request_kwargs"]["cookies"] == {
        "theme": "dark",
    }

    assert captured["saved_cookies"] == {
        "cookies": {
            "session": "abc123",
        },
        "filename": "cookies.txt",
    }

    assert captured["printed"] == {
        "output": "formatted response",
        "filename": "response.bin",
        "content": b"response bytes",
    }


def test_main_preserves_explicit_method(monkeypatch):
    args = make_args(
        method="DELETE",
        data="body",
    )

    captured = prepare_successful_main(
        monkeypatch,
        args,
    )

    main_module.main()

    assert args.method == "DELETE"
    assert captured["request_kwargs"]["method"] == "DELETE"


@pytest.mark.parametrize(
    (
        "error",
        "expected_output",
    ),
    [
        (
            InvalidURLException("Invalid URL"),
            "mycurl: Invalid URL",
        ),
        (
            InvalidMethodException("Invalid method"),
            "mycurl: Invalid method",
        ),
        (
            InvalidHeaderException("Invalid header"),
            "mycurl: Invalid header",
        ),
        (
            InvalidTimeoutException("Invalid timeout"),
            "mycurl: Invalid timeout",
        ),
        (
            RequestTimeoutException("ignored"),
            "mycurl: Request timed out",
        ),
        (
            ConnectionException("ignored"),
            "mycurl: Connection failed",
        ),
        (
            FileUploadException("Upload failed"),
            "mycurl: Upload failed",
        ),
        (
            InvalidCookieException("Invalid cookie"),
            "mycurl: Invalid cookie",
        ),
        (
            FileWriteException("File write failed"),
            "mycurl: File write failed",
        ),
        (
            TooManyRedirectsException(
                "Too many redirects"
            ),
            "mycurl: Too many redirects",
        ),
        (
            TLSException("TLS failed"),
            "mycurl: TLS failed",
        ),
        (
            InvalidAuthException("Invalid auth"),
            "mycurl: Invalid auth",
        ),
        (
            InvalidFormException("Invalid form"),
            "mycurl: Invalid form",
        ),
        (
            RequestFailedException("Request failed"),
            "mycurl: Request failed",
        ),
    ],
)
def test_main_handles_custom_exceptions(
    monkeypatch,
    capsys,
    error,
    expected_output,
):
    def raise_error():
        raise error

    monkeypatch.setattr(
        main_module,
        "parse_args",
        raise_error,
    )

    with pytest.raises(SystemExit) as exit_info:
        main_module.main()

    assert exit_info.value.code == 1

    captured = capsys.readouterr()

    assert captured.out.strip() == expected_output
    assert "Traceback" not in captured.err


def test_main_file_entrypoint(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--version",
        ],
    )

    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(
            str(MAIN_FILE),
            run_name="__main__",
        )

    assert exit_info.value.code == 0

    captured = capsys.readouterr()

    assert "MyCurl 2.1" in captured.out