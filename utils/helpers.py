from utils.errors import (
    FileUploadException,
    InvalidCookieException,
    FileWriteException,
)

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

    for pair in cookie.split(";"):
        pair = pair.strip()

        if "=" not in pair:
            raise InvalidCookieException(
                f"Invalid cookie format: {pair}\n"
                "Expected: name=value"
            )

        key, value = pair.split("=", 1)
        key = key.strip()

        if not key:
            raise InvalidCookieException(
                f"Invalid cookie format: {pair}\n"
                "Cookie name cannot be empty."
            )

        cookies[key] = value.strip()

    return cookies


def parse_forms(forms):
    data = {}
    files = {}

    if not forms:
        return data, files
    
    for form in forms:

        key, value = form.split("=", 1)

        if value.startswith("@"):
            filename = value[1:]

            try:
                files[key] = open(filename, "rb")
            
            except FileNotFoundError:
                raise FileUploadException(
                    f"File not found: {filename}"
                )
        
        else:
            data[key] = value

    return data, files


def save_cookies(cookies, filename):
    if not filename:
        return

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("# Netscape HTTP Cookie File\n")

            for cookie in cookies:
                domain = cookie.domain or ""
                include_subdomains = (
                    "TRUE" if domain.startswith(".") else "FALSE"
                )
                path = cookie.path or "/"
                secure = "TRUE" if cookie.secure else "FALSE"
                expires = int(cookie.expires) if cookie.expires else 0

                file.write(
                    f"{domain}\t"
                    f"{include_subdomains}\t"
                    f"{path}\t"
                    f"{secure}\t"
                    f"{expires}\t"
                    f"{cookie.name}\t"
                    f"{cookie.value}\n"
                )

    except OSError as error:
        raise FileWriteException(
            f"Could not write file: {filename}\n"
            f"{error}"
        ) from error