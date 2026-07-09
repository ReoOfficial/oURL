from urllib.parse import urlparse

from core.methods import SUPPORTED_METHODS

from utils.errors import (
    InvalidURLException,
    InvalidMethodException,
    InvalidHeaderException,
    InvalidTimeoutException,
)

def validate(args):
    validate_url(args.url)
    validate_method(args.method)
    validate_headers(args.header)
    validate_timeout(args.max_time)

    return args


def validate_url(url):
    parsed = urlparse(url)

    if not parsed.scheme or not parsed.netloc:
        raise InvalidURLException
    

def validate_method(method):
    if method.upper() not in SUPPORTED_METHODS:
        raise InvalidMethodException
    

def validate_headers(headers):
    for header in headers:
        if ":" not in headers:
            raise InvalidHeaderException(
                f"Invalid header format{header}"
            )
        

def validate_timeout(timeout):
    if timeout <= 0:
        raise InvalidTimeoutException(
            "Timeout must be greater than zero."
        )