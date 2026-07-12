import pytest

from output.printer import print_response
from utils.errors import FileWriteException


def test_invalid_output_path():
    with pytest.raises(FileWriteException):
        print_response(
            "Hello",
            "folder_that_does_not_exist/output.txt",
            b"Hello",
        )


def test_binary_output_is_written_exactly(tmp_path):
    output_file = tmp_path / "image.png"

    binary_content = b"\x89PNG\r\n\x1a\n\x00\x00test"

    print_response(
        "This formatted text should not be saved",
        str(output_file),
        binary_content,
    )

    assert output_file.read_bytes() == binary_content