import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        prog="mycurl",
        usage="mycurl [options] URL",
        description=(
            "A lightweight cURL-like command-line HTTP client "
            "written in Python."
        ),
        epilog=(
            "Examples:\n"
            "  mycurl https://example.com\n"
            "  mycurl -v https://example.com\n"
            "  mycurl -X POST -d \"name=Reo\" https://example.com\n"
            "  mycurl -H \"Accept: application/json\" https://example.com\n"
            "  mycurl -F \"file=@example.txt\" https://example.com/upload\n"
            "  mycurl -L -o response.txt https://example.com"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="MyCurl 2.1",
    )

    target_group = parser.add_argument_group("target")

    target_group.add_argument(
        "url",
        metavar="URL",
        help="Target HTTP or HTTPS URL",
    )

    request_group = parser.add_argument_group("request options")

    request_group.add_argument(
        "-X",
        "--request",
        dest="method",
        metavar="METHOD",
        default=None,
        help="Specify the HTTP request method",
    )

    request_group.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="HEADER",
        help='Add a request header, for example "Accept: application/json"',
    )

    request_group.add_argument(
        "-d",
        "--data",
        metavar="DATA",
        help="Send request body data; implies POST unless -X is used",
    )

    request_group.add_argument(
        "-F",
        "--form",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="Add multipart form data or a file using NAME=@FILE",
    )

    request_group.add_argument(
        "-I",
        "--head",
        action="store_true",
        help="Send a HEAD request and display response headers",
    )

    authentication_group = parser.add_argument_group(
        "authentication and cookies"
    )

    authentication_group.add_argument(
        "-u",
        "--user",
        metavar="USER:PASSWORD",
        help="Use HTTP Basic Authentication",
    )

    authentication_group.add_argument(
        "-b",
        "--cookie",
        metavar="COOKIE",
        help='Send cookies, for example "session=abc123"',
    )

    authentication_group.add_argument(
        "-c",
        "--cookie-jar",
        metavar="FILE",
        help="Save received cookies to a file",
    )

    connection_group = parser.add_argument_group("connection options")

    connection_group.add_argument(
        "--max-time",
        type=float,
        default=15.0,
        metavar="SECONDS",
        help="Maximum request time in seconds (default: 15)",
    )

    connection_group.add_argument(
        "-L",
        "--location",
        action="store_true",
        help="Follow HTTP redirects",
    )

    connection_group.add_argument(
        "-k",
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification",
    )

    output_group = parser.add_argument_group("output options")

    output_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display request and response details",
    )

    output_group.add_argument(
        "-A",
        "--user-agent",
        metavar="USER_AGENT",
        help="Set a custom User-Agent header",
    )

    output_group.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Write the response to a file",
    )

    return parser.parse_args()