def print_response(output, filename):
    if filename:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(output)

        print(f"Response saved to '{filename}'")

    else:
        print(output)