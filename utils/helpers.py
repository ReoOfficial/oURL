from utils.errors import FileUploadException

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
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write("# Netscape HTTP Cookie FIle\n")

        for cookie in cookies:
            domain = cookie.domain or ""
            include_subdomains = "TRUE" if domain.startswith(".") else "FALSE"
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