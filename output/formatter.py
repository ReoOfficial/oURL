import json
from urllib.parse import urlparse

def format_body(body):
    try:
        parsed = json.loads(body)
        return json.dumps(parsed, indent=4, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        return body

def format_response(request, response):
    output = ""

    if request.verbose:

        parsed = urlparse(request.url)

        path = parsed.path or "/"

        if parsed.query:
            path += f"?{parsed.query}"

        method = "HEAD" if request.head else request.method

        output += f"> {method} {path} HTTP/1.1\n"

        output += f"> Host: {parsed.netloc}\n"

        headers = response.get_sent_headers()

        if "User-Agent" in headers:
            output += f"> User-Agent: {headers['User-Agent']}\n"

        if "Accept" in headers:
            output += f"> Accept: {headers['Accept']}\n"

        for key, value in headers.items():

            if key in ("User-Agent", "Accept"):
                continue
            
            output += f"> {key}: {value}\n"

        if request.body:
            output += "\n"
            output += str(request.body)
            output += "\n"

        output += "\n"

        output += (
            f"< HTTP/1.1 "
            f"{response.get_status_code()} "
            f"{response.get_reason()}\n"
        )


        for key, value in response.get_headers().items():
            output += f"< {key}: {value}\n"

        output += "\n"

    elif request.head:

        output+= (
            f"HTTP/1.1 "
            f"{response.get_status_code()} "
            f"{response.get_reason()}\n"
        )

        for key, value in response.get_headers().items():
            output += f"{key}: {value}\n"

        output += "\n"

    if not request.head:
        output += format_body(response.get_body())

    if request.verbose:
        output += f"\n\nTime: {response.get_elapsed_seconds():.3f}s"
        output += f"\nSize: {response.get_size()} bytes"

    return output