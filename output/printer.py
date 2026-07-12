from utils.errors import FileWriteException


def print_response(output, filename=None, content=None):
    if filename:
        try:
            with open(filename, "wb") as file:
                file.write(content)

        except OSError as error:
            raise FileWriteException(
                f"Could not write file: {filename}\n"
                f"{error}"
            ) from error

        print(f"Response saved to '{filename}'")

    else:
        print(output)