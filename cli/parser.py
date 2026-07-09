import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        prog="mycurl",
        description="A custom cURL implementation in python."
    )
    
    parser.add_argument(
        "url",
        help="Target URL"
    )

    parser.add_argument(
        "-X",
        "--request",
        dest="method",
        help="HTTP Method"
    )

    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        help="HTTP Headers"
    )

    parser.add_argument(
        "-d",
        "--data",
        help="Request Body"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose Output"
    )

    parser.add_argument(
        "--max-time",
        type=int,
        default=15,
        help="Request Timeout"
    )

    parser.add_argument(
        "-L",
        "--location",
        action="store_true",
        help="Follow Redirects"
    )

    parser.add_argument(
        "-k",
        "--insecure",
        action="store_true",
        help="Ignore SSL Verifications"
    )

    parser.add_argument(
        "-u",
        "--user",
        help="Username:Password"
    )

    parser.add_argument(
        "-A",
        "--user-agent",
        help="Custom User-Agent"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Save responseto file"
    )

    parser.add_argument(
        "-I",
        "--head",
        action="store_true",
        help="Send HEAD request"
    )

    parser.add_argument(
        "-b",
        "--cookie",
        help="Send Cookies"
    )

    parser.add_argument(
        "-c",
        "--cookie-jar",
        help="Save Cookies"
    )

    parser.add_argument(
        "-F",
        "--form",
        action="append",
        default=[],
        help="Multiple Form Date"
    )

    return parser.parse_args()