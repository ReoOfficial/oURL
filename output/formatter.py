from urllib.parse import urlparse


def format_response(request, response):
    output = ""

    if request.verbose:

        parsed = urlparse(request.url)
        path = parsed.path or "/"

        output += f"> {request.method} {path} HTTP/1.1\n"

        output += f"> Host: {parsed.netloc}\n"

        if request.user_agent:
            output += f"> User-Agent: {request.user_agent}\n"
        else:
            output += "> User-Agent: MyCurl/1.0\n"

        output += "> Accpet: */*\n"

        for key, value in request.headers.items():
            output += f"> {key}: {value}\n"

        output += "\n"

        output += (
            f"< HTTP {response.get_status_code()} "
            f"{response.get_reason()}\n"
        )


        for key, value in response.get_headers().items():
            output += f"< {key}: {value}\n"

        output += "\n"

    if not request.head:
        output += response.get_body()

    return output