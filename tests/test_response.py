from datetime import timedelta
from types import SimpleNamespace

from core.response import Response


def make_raw_response():
    return SimpleNamespace(
        status_code=200,
        reason="OK",
        headers={
            "Content-Type": "application/json",
        },
        text='{"message": "hello"}',
        content=b'{"message": "hello"}',
        url="https://example.com/final",
        elapsed=timedelta(seconds=1.25),
        cookies={
            "session": "abc123",
        },
        history=[
            "redirect-response",
        ],
    )


def test_response_getters():
    raw_response = make_raw_response()

    sent_headers = {
        "User-Agent": "MyCurl/2.1",
        "Accept": "*/*",
    }

    response = Response(
        raw_response,
        sent_headers=sent_headers,
    )

    assert response.get_status_code() == 200
    assert response.get_reason() == "OK"

    assert response.get_headers() == {
        "Content-Type": "application/json",
    }

    assert response.get_body() == '{"message": "hello"}'
    assert response.get_content() == b'{"message": "hello"}'

    assert response.get_url() == "https://example.com/final"
    assert response.get_elapsed() == timedelta(seconds=1.25)

    assert response.get_cookies() == {
        "session": "abc123",
    }

    assert response.get_history() == [
        "redirect-response",
    ]

    assert response.get_sent_headers() == sent_headers


def test_response_calculated_values():
    response = Response(
        make_raw_response(),
        sent_headers={},
    )

    assert response.get_elapsed_seconds() == 1.25
    assert response.get_size() == len(b'{"message": "hello"}')