import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_FILE = PROJECT_ROOT / "main.py"


def run_mycurl(*arguments):
    return subprocess.run(
        [
            sys.executable,
            str(MAIN_FILE),
            *arguments,
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_version_command():
    result = run_mycurl("--version")

    assert result.returncode == 0
    assert "MyCurl 2.1" in result.stdout


def test_help_command():
    result = run_mycurl("--help")

    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "--verbose" in result.stdout


def test_invalid_url_exits_with_error():
    result = run_mycurl("example.com")

    assert result.returncode != 0
    assert "Invalid URL" in result.stdout
    assert "Traceback" not in result.stderr


def test_invalid_header_exits_with_error():
    result = run_mycurl(
        "-H",
        "WrongHeader",
        "https://example.com",
    )

    assert result.returncode != 0
    assert "Invalid header format" in result.stdout
    assert "Traceback" not in result.stderr


def test_invalid_cookie_exits_with_error():
    result = run_mycurl(
        "-b",
        "malformed_cookie",
        "https://example.com",
    )

    assert result.returncode != 0
    assert "Invalid cookie format" in result.stdout
    assert "Traceback" not in result.stderr


def test_invalid_auth_exits_with_error():
    result = run_mycurl(
        "-u",
        "missing_password",
        "https://example.com",
    )

    assert result.returncode != 0
    assert "Invalid authentication format" in result.stdout
    assert "Traceback" not in result.stderr


def test_invalid_form_exits_with_error():
    result = run_mycurl(
        "-F",
        "missing_equals_sign",
        "https://example.com",
    )

    assert result.returncode != 0
    assert "Invalid form format" in result.stdout
    assert "Traceback" not in result.stderr


def test_invalid_timeout_exits_with_error():
    result = run_mycurl(
        "--max-time",
        "0",
        "https://example.com",
    )

    assert result.returncode != 0
    assert "Timeout must be greater than zero" in result.stdout
    assert "Traceback" not in result.stderr


def test_nonexistent_upload_exits_with_error():
    result = run_mycurl(
        "-F",
        "file=@file_that_does_not_exist.txt",
        "https://example.com",
    )

    assert result.returncode != 0
    assert "file_that_does_not_exist.txt" in result.stdout
    assert "Traceback" not in result.stderr