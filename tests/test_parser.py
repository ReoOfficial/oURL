import sys

from cli.parser import parse_args


def test_basic_url(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["mycurl", "https://example.com"],
    )

    args = parse_args()

    assert args.url == "https://example.com"


def test_default_values(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["mycurl", "https://example.com"],
    )

    args = parse_args()

    assert args.method is None
    assert args.header == []
    assert args.verbose is False
    assert args.location is False
    assert args.insecure is False
    assert args.max_time == 15.0


def test_decimal_timeout(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mycurl",
            "--max-time",
            "5.5",
            "https://example.com",
        ],
    )

    args = parse_args()

    assert args.max_time == 5.5
    assert isinstance(args.max_time, float)


def test_custom_method(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mycurl",
            "-X",
            "POST",
            "https://example.com",
        ],
    )

    args = parse_args()

    assert args.method == "POST"


def test_multiple_headers(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mycurl",
            "-H",
            "Accept: application/json",
            "-H",
            "X-Test: value",
            "https://example.com",
        ],
    )

    args = parse_args()

    assert args.header == [
        "Accept: application/json",
        "X-Test: value",
    ]


def test_request_body(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mycurl",
            "-d",
            "name=Reo",
            "https://example.com",
        ],
    )

    args = parse_args()

    assert args.data == "name=Reo"


def test_verbose_and_redirects(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mycurl",
            "-v",
            "-L",
            "https://example.com",
        ],
    )

    args = parse_args()

    assert args.verbose is True
    assert args.location is True


def test_authentication_and_cookies(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mycurl",
            "-u",
            "Reo:secret",
            "-b",
            "session=abc123",
            "https://example.com",
        ],
    )

    args = parse_args()

    assert args.user == "Reo:secret"
    assert args.cookie == "session=abc123"


def test_multiple_forms(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mycurl",
            "-F",
            "name=Reo",
            "-F",
            "role=developer",
            "https://example.com",
        ],
    )

    args = parse_args()

    assert args.form == [
        "name=Reo",
        "role=developer",
    ]


def test_head_and_output(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mycurl",
            "-I",
            "-o",
            "response.txt",
            "https://example.com",
        ],
    )

    args = parse_args()

    assert args.head is True
    assert args.output == "response.txt"