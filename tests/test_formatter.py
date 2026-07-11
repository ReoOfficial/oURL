from types import SimpleNamespace

from output.formatter import format_body, format_response


class FakeResponse:
    def get_status_code(self):
        return 200

    def get_reason(self):
        return "OK"

    def get_headers(self):
        return {
            "Content-Type": "application/json"
        }

    def get_body(self):
        return '{"message":"hello"}'

    def get_sent_headers(self):
        return {
            "User-Agent": "MyCurl/2.0",
            "Accept": "*/*",
        }

    def get_elapsed_seconds(self):
        return 0.125

    def get_size(self):
        return 19


def make_request(**changes):
    values = {
        "url": "https://example.com/test?name=Reo",
        "method": "GET",
        "verbose": False,
        "head": False,
        "body": None,
    }

    values.update(changes)

    return SimpleNamespace(**values)


def test_format_json_body():
    result = format_body('{"message":"hello"}')

    assert '"message": "hello"' in result
    assert "\n" in result


def test_format_plain_text_body():
    result = format_body("Hello world")

    assert result == "Hello world"


def test_normal_response_displays_body():
    request = make_request()
    response = FakeResponse()

    result = format_response(request, response)

    assert '"message": "hello"' in result
    assert "HTTP/1.1" not in result
    assert "Time:" not in result


def test_verbose_response_displays_request_details():
    request = make_request(verbose=True)
    response = FakeResponse()

    result = format_response(request, response)

    assert "> GET /test?name=Reo HTTP/1.1" in result
    assert "> Host: example.com" in result
    assert "> User-Agent: MyCurl/2.0" in result
    assert "< HTTP/1.1 200 OK" in result


def test_verbose_response_displays_statistics():
    request = make_request(verbose=True)
    response = FakeResponse()

    result = format_response(request, response)

    assert "Time: 0.125s" in result
    assert "Size: 19 bytes" in result


def test_verbose_post_displays_request_body():
    request = make_request(
        method="POST",
        verbose=True,
        body="name=Reo",
    )

    response = FakeResponse()

    result = format_response(request, response)

    assert "> POST /test?name=Reo HTTP/1.1" in result
    assert "name=Reo" in result


def test_head_displays_headers_without_body():
    request = make_request(head=True)
    response = FakeResponse()

    result = format_response(request, response)

    assert "HTTP/1.1 200 OK" in result
    assert "Content-Type: application/json" in result
    assert '"message": "hello"' not in result


def test_verbose_head_displays_head_method():
    request = make_request(
        verbose=True,
        head=True,
    )

    response = FakeResponse()

    result = format_response(request, response)

    assert "> HEAD /test?name=Reo HTTP/1.1" in result
    assert '"message": "hello"' not in result