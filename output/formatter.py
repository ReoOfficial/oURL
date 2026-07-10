def format_response(request, response):
    output = ""

    if request.verbose:
        output += f"> {request.method} {request.url}\n"

        for key, value in request.headers.items():
            output += f"> {key}: {value}\n"

        output += "\n"

        output += f"< HTTP {response.get_status_code()} {response.get_reason()}\n"


        for key, value in response.get_headers().items():
            output += f"< {key}: {value}\n"

        output += "\n"

    if not request.head:
        output += response.get_body()

    return output