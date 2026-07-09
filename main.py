from cli.parser import parse_args
from cli.validator import validate
from core.request import Request
from core.client import Client
from output.formatter import format_response
from output.printer import print_response

args = parse_args()

validate(args)

request = Request(
    method=args.method,
    url=args.url,
    headers=args.header,
    body=args.data,
    timeout=args.max_time
)


client = Client()

response = client.send(request)

output = format_response(response)

print_response(output)