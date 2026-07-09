def format_response(response):
    output = ""

    output += f"Status: {response.status_code}\n\n"

    output += "Headers:\n"

    for key, value in response.headers.items():
        output += f"{key}: {value}\n"

    output += "\nbody:\n"

    output += response.body

    return output