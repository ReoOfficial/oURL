import sys

from cli.parser import parse_args
from cli.validator import validate

from core.request import Request
from core.client import Client

from output.formatter import format_response
from output.printer import print_response

from utils.helpers import (
    parse_headers,
    parse_auth,
    parse_cookies,
    parse_forms,
    save_cookies,
)

from utils.errors import (
    InvalidURLException,
    InvalidMethodException,
    InvalidHeaderException,
    InvalidTimeoutException,
    RequestTimeoutException,
    ConnectionException,
    FileUploadException,
    InvalidCookieException,
    FileWriteException,
    TooManyRedirectsException,
)

try:
    args = parse_args()

    if args.method is None:

        if args.data or args.form:
            args.method = "POST"
    
        else:
            args.method = "GET"

    validate(args)

    form_data, form_files = parse_forms(args.form)

    request = Request(
        method=args.method,
        url=args.url,
        headers=parse_headers(args.header),
        body=args.data,
        timeout=args.max_time,

        verbose=args.verbose,
        follow_redirects=args.location,
        insecure=args.insecure,

        auth=parse_auth(args.user),
        user_agent=args.user_agent,

        output=args.output,
        head=args.head,

        cookies=parse_cookies(args.cookie),
        cookie_jar=args.cookie_jar,

        form_data=form_data,
        form_files=form_files,
    )


    client = Client()

    response = client.send(request)

    if args.cookie_jar:
        save_cookies(
            response.get_cookies(),
            args.cookie_jar
        )

    output = format_response(request, response)

    print_response(
        output,
        args.output,
        response.get_content(),
        )

except InvalidURLException as e:
    print(f"mycurl: {e}")
    sys.exit(1)

except InvalidMethodException as e:
    print(f"mycurl: {e}")
    sys.exit(1)

except InvalidHeaderException as e:
    print(f"mycurl: {e}")
    sys.exit(1)

except InvalidTimeoutException as e:
    print(f"mycurl: {e}")
    sys.exit(1)

except RequestTimeoutException:
    print("mycurl: Request timed out")
    sys.exit(1)

except ConnectionException:
    print("mycurl: Connection failed")

except FileUploadException as e :
    print(f"mycurl: {e}")
    sys.exit(1)

except InvalidCookieException as e:
    print(f"mycurl: {e}")
    sys.exit(1)

except FileWriteException as error:
    print(f"mycurl: {error}")
    sys.exit(1)

except TooManyRedirectsException as error:
    print(f"mycurl: {error}")
    sys.exit(1)