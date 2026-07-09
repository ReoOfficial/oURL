def format_response(response):
    output = ""

    output += f"HTTP Status: {response.get_status_code()} {response.get_reason()}\n\n"

    output += "Headers:\n"

    for key, value in response.get_headers().items():
        output += f"{key}: {value}\n"

    output += "\nbody:\n"

    output += response.get_body()

    return output