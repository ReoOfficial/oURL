from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests

import core.client as client_module
from core.client import Client
from core.response import Response
from utils.errors import (
    RequestTimeoutException,
    ConnectionException,
    TooManyRedirectsException,
    TLSException,
    RequestFailedException,
)


def test_unexpected_request_exception_is_converted(monkeypatch):
    def fake_request(**kwargs):
        raise requests.exceptions.RequestException(
            "Unexpected transport error"
        )

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    with pytest.raises(
        RequestFailedException,
        match="Request failed: Unexpected transport error",
    ):
        Client().send(make_request())

def test_ssl_exception_is_converted(monkeypatch):
    def fake_request(**kwargs):
        raise requests.exceptions.SSLError

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    with pytest.raises(
        TLSException,
        match="TLS certificate verification failed",
    ):
        Client().send(make_request())


def test_too_many_redirects_is_converted(monkeypatch):
    def fake_request(**kwargs):
        raise requests.exceptions.TooManyRedirects

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    with pytest.raises(
        TooManyRedirectsException,
        match="Too many redirects",
    ):
        Client().send(make_request())

def make_request(**changes):
    values = {
        "method": "GET",
        "url": "https://example.com",
        "headers": {},
        "body": None,
        "form_data": {},
        "form_files": {},
        "auth": None,
        "cookies": {},
        "timeout": 15,
        "insecure": False,
        "follow_redirects": False,
        "user_agent": None,
        "head": False,
    }

    values.update(changes)

    return SimpleNamespace(**values)


def make_http_response(sent_headers=None):
    return SimpleNamespace(
        status_code=200,
        reason="OK",
        headers={"Content-Type": "text/plain"},
        text="Hello",
        content=b"Hello",
        url="https://example.com",
        elapsed=timedelta(seconds=0.1),
        cookies={},
        history=[],
        request=SimpleNamespace(
            headers=sent_headers or {}
        ),
    )


def test_send_get_request(monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return make_http_response(kwargs["headers"])

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    result = Client().send(make_request())

    assert isinstance(result, Response)
    assert captured["method"] == "GET"
    assert captured["url"] == "https://example.com"
    assert captured["timeout"] == 15
    assert captured["verify"] is True
    assert captured["allow_redirects"] is False


def test_head_option_sends_head_request(monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return make_http_response(kwargs["headers"])

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    Client().send(
        make_request(
            method="GET",
            head=True,
        )
    )

    assert captured["method"] == "HEAD"


def test_default_user_agent(monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return make_http_response(kwargs["headers"])

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    Client().send(make_request())

    assert (
        captured["headers"]["User-Agent"]
        == "MyCurl/2.0"
    )


def test_custom_user_agent(monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return make_http_response(kwargs["headers"])

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    Client().send(
        make_request(user_agent="CustomAgent/1.0")
    )

    assert (
        captured["headers"]["User-Agent"]
        == "CustomAgent/1.0"
    )


def test_body_adds_default_content_type(monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return make_http_response(kwargs["headers"])

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    Client().send(
        make_request(
            method="POST",
            body="name=Reo",
        )
    )

    assert captured["data"] == "name=Reo"
    assert captured["headers"]["Content-Type"] == (
        "application/x-www-form-urlencoded"
    )


def test_custom_content_type_is_preserved(monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return make_http_response(kwargs["headers"])

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    Client().send(
        make_request(
            method="POST",
            body='{"name":"Reo"}',
            headers={
                "Content-Type": "application/json"
            },
        )
    )

    assert (
        captured["headers"]["Content-Type"]
        == "application/json"
    )


def test_form_data_is_sent_instead_of_body(monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return make_http_response(kwargs["headers"])

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    Client().send(
        make_request(
            method="POST",
            body="ignored body",
            form_data={"name": "Reo"},
        )
    )

    assert captured["data"] == {"name": "Reo"}

    assert (
        "Content-Type" not in captured["headers"]
    )


def test_request_options_are_forwarded(monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return make_http_response(kwargs["headers"])

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    Client().send(
        make_request(
            timeout=5,
            insecure=True,
            follow_redirects=True,
            auth=("Reo", "secret"),
            cookies={"session": "abc123"},
        )
    )

    assert captured["timeout"] == 5
    assert captured["verify"] is False
    assert captured["allow_redirects"] is True
    assert captured["auth"] == ("Reo", "secret")
    assert captured["cookies"] == {
        "session": "abc123"
    }


def test_prepared_headers_are_stored(monkeypatch):
    prepared_headers = {
        "User-Agent": "MyCurl/2.0",
        "Content-Length": "8",
        "Content-Type": (
            "application/x-www-form-urlencoded"
        ),
    }

    def fake_request(**kwargs):
        return make_http_response(prepared_headers)

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    result = Client().send(
        make_request(
            method="POST",
            body="name=Reo",
        )
    )

    assert result.get_sent_headers() == prepared_headers


def test_timeout_exception_is_converted(monkeypatch):
    def fake_request(**kwargs):
        raise requests.exceptions.Timeout

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    with pytest.raises(
        RequestTimeoutException,
        match="Request timed out",
    ):
        Client().send(make_request())


def test_connection_exception_is_converted(monkeypatch):
    def fake_request(**kwargs):
        raise requests.exceptions.ConnectionError

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    with pytest.raises(
        ConnectionException,
        match="Connection failed",
    ):
        Client().send(make_request())


def test_uploaded_files_are_closed(monkeypatch):
    uploaded_file = Mock()

    def fake_request(**kwargs):
        return make_http_response(kwargs["headers"])

    monkeypatch.setattr(
        client_module.requests,
        "request",
        fake_request,
    )

    Client().send(
        make_request(
            method="POST",
            form_files={"file": uploaded_file},
        )
    )

    uploaded_file.close.assert_called_once()