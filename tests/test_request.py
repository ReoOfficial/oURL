from core.request import Request


def test_request_stores_all_values():
    upload_file = object()

    request = Request(
        method="POST",
        url="https://example.com/upload",
        headers={
            "Content-Type": "application/json",
        },
        body='{"name": "Reo"}',
        timeout=5.5,
        verbose=True,
        follow_redirects=True,
        insecure=True,
        auth=(
            "user",
            "password",
        ),
        user_agent="CustomAgent/1.0",
        output="response.bin",
        head=False,
        cookies={
            "session": "abc123",
        },
        cookie_jar="cookies.txt",
        form_data={
            "name": "Reo",
        },
        form_files={
            "file": upload_file,
        },
    )

    assert request.method == "POST"
    assert request.url == "https://example.com/upload"

    assert request.headers == {
        "Content-Type": "application/json",
    }

    assert request.body == '{"name": "Reo"}'
    assert request.timeout == 5.5
    assert request.verbose is True
    assert request.follow_redirects is True
    assert request.insecure is True

    assert request.auth == (
        "user",
        "password",
    )

    assert request.user_agent == "CustomAgent/1.0"
    assert request.output == "response.bin"
    assert request.head is False

    assert request.cookies == {
        "session": "abc123",
    }

    assert request.cookie_jar == "cookies.txt"

    assert request.form_data == {
        "name": "Reo",
    }

    assert request.form_files == {
        "file": upload_file,
    }


def test_request_default_collection_values():
    request = Request(
        method="GET",
        url="https://example.com",
        headers=None,
        body=None,
        timeout=15.0,
        verbose=False,
        follow_redirects=False,
        insecure=False,
        auth=None,
        user_agent=None,
        output=None,
        head=False,
        cookies=None,
        cookie_jar=None,
        form_data=None,
        form_files=None,
    )

    assert request.headers == {}
    assert request.cookies is None
    assert request.form_data is None
    assert request.form_files == {}