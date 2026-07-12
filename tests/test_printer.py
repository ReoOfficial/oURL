import pytest

from output.printer import print_response
from utils.errors import FileWriteException


def test_invalid_output_path():
    with pytest.raises(FileWriteException):
        print_response(
            "Hello",
            "folder_that_does_not_exist/output.txt",
        )