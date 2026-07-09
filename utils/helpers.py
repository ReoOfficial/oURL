def parse_headers(headers):
    parsed_headers = {}

    for header in headers:
        key, value = header.split(":", 1)

        parsed_headers[key.strip()] = value.strip()

    return parsed_headers