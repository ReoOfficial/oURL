from utils.errors import FileWriteException


def print_response(output, filename):
    if filename:
        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(output)

        except OSError as error:
            raise FileWriteException(
                f"Could not write file: {filename}\n"
                f"{error}"
            ) from error

        print(f"Response saved to '{filename}'")

    else:
        print(output)