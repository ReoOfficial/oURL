from urllib.parse import urlparse

from core.methods import SUPPORTED_METHODS

from utils.errors import (
    InvalidURLException,
    InvalidMethodException,
    InvalidHeaderException,
    InvalidTimeoutException,
    InvalidAuthException,
    InvalidFormException
)

def validate(args):
    validate_url(args.url)
    validate_method(args.method)
    validate_headers(args.header)
    validate_timeout(args.max_time)
    validate_auth(args.user)
    validate_forms(args.form)

    return args


def validate_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise InvalidURLException(
            f"Invalid URL: {url}\n"
            "Expected an HTTP or HTTPS URL."
        )
    

def validate_method(method):
    # No -X means the client will use its default method
    if method is None:
        return

    if method.upper() not in SUPPORTED_METHODS:
        raise InvalidMethodException(
            f"Unsupported method: {method}"
        )
    

def validate_headers(headers):
    for header in headers:
        if ":" not in header:
            raise InvalidHeaderException(
                f"Invalid header format: {header}\n"
                "Expected: Key: Value"
            )

        name, _ = header.split(":", 1)

        if not name.strip():
            raise InvalidHeaderException(
                f"Invalid header format: {header}\n"
                "Header name cannot be empty."
            )
        

def validate_timeout(timeout):
    if timeout <= 0:
        raise InvalidTimeoutException(
            "Timeout must be greater than zero."
        )
    
def validate_auth(auth):
    if not auth:
        return

    if ":" not in auth:
        raise InvalidAuthException(
            "Invalid authentication format\n"
            "Expected: username:password"
        )

    username, _ = auth.split(":", 1)

    if not username.strip():
        raise InvalidAuthException(
            "Invalid authentication format\n"
            "Username cannot be empty."
        )
    
def validate_forms(forms):
    for form in forms:
        if "=" not in form:
            raise InvalidFormException(
                f"Invalid form format: {form}\n"
                "Expected: name=value or name=@filename"
            )

        name, _ = form.split("=", 1)

        if not name.strip():
            raise InvalidFormException(
                f"Invalid form format: {form}\n"
                "Form field name cannot be empty."
            )