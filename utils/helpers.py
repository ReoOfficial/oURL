def parse_headers(headers):
    parsed_headers = {}

    for header in headers:
        key, value = header.split(":", 1)

        parsed_headers[key.strip()] = value.strip()

    return parsed_headers

def parse_auth(auth):
    if not auth:
        return None
    
    username, password = auth.split(":", 1)
    
    return username, password

def parse_cookies(cookie):
    if not cookie:
        return {}
    
    cookies = {}

    pairs = cookie.split(";")

    for pair in pairs:
        key, value = pair.split("=", 1)
        cookies[key.strip()] = value.strip()

    return cookies


def parse_forms(forms):
    if not forms:
        return {}
    
    data = {}

    for form in forms:
        key, value = form.split("=", 1)
        data[key] = value

    return data