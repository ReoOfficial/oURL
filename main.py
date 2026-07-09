from cli.parser import parse_args
from cli.validator import validate
from core.request import Request
from core.client import Client
from output.formatter import format_response
from output.printer import print_response
from utils.helpers import (
    parse_headers,
    parse_headers,
    parse_auth,
    parse_cookies,
    parse_forms,
)

args = parse_args()

validate(args)

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

    form=parse_forms(args.form)
)


client = Client()

response = client.send(request)

output = format_response(response)

print_response(output, args.output)