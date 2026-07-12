# MyCurl 2.1

MyCurl is a lightweight, modular command-line HTTP client inspired by cURL.

It supports common HTTP and HTTPS workflows including custom methods, headers,
request bodies, multipart forms, file uploads, authentication, cookies,
redirects, TLS control, timeouts, verbose output, HEAD requests, JSON
pretty-printing, and binary-safe file downloads.

**Repository:** `ReoOfficial/oURL`  
**Language:** Python  
**Current version:** `MyCurl 2.1`  
**Test suite:** `109 passing tests`  
**Measured coverage:** `100%`

---

## Features

### HTTP requests

- `GET`
- `POST`
- `PUT`
- `PATCH`
- `DELETE`
- `HEAD`
- `OPTIONS`
- Custom methods through `-X` / `--request`
- Automatic `GET` or `POST` selection when no method is supplied

### Request data

- Custom headers with `-H`
- Raw request bodies with `-d`
- Form fields with `-F`
- File uploads with `-F name=@filename`
- Automatic form content type when appropriate
- Custom User-Agent with `-A`

### Authentication and cookies

- Basic authentication with `-u username:password`
- Send cookies with `-b`
- Save response cookies with `-c`
- Netscape-compatible cookie-jar output

### Connection behavior

- Follow redirects with `-L`
- Disable TLS certificate verification with `-k`
- Integer and decimal timeout values with `--max-time`
- Dedicated timeout, redirect, TLS, connection, and generic request errors

### Output

- Normal response-body output
- Verbose request and response details with `-v`
- HEAD requests with `-I`
- JSON pretty-printing
- Request timing
- Response size in bytes
- Binary-safe downloads with `-o`
- Prepared outgoing headers in verbose mode

### Reliability

- Clean non-zero exit codes for handled errors
- No raw tracebacks for expected CLI failures
- Upload-file cleanup after success or failure
- Cleanup after partially failed multi-file uploads
- Safe output-file and cookie-file error handling
- Dedicated validation errors for URLs, methods, headers, timeouts,
  authentication, forms, and cookies
- Fallback handling for unexpected Requests exceptions

---

## Requirements

- Python 3
- `requests`
- `pytest`
- `pytest-cov`

The current project was tested with Python `3.14.6`.

---

## Installation

Clone the repository:

```powershell
git clone https://github.com/ReoOfficial/oURL.git
cd oURL
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

---

## Basic usage

```powershell
python main.py [OPTIONS] URL
```

Simple GET request:

```powershell
python main.py https://example.com
```

Show help:

```powershell
python main.py --help
```

Show the current version:

```powershell
python main.py --version
```

Expected output:

```text
MyCurl 2.1
```

---

## Command-line options

| Option | Description |
|---|---|
| `URL` | Target HTTP or HTTPS URL |
| `-X`, `--request METHOD` | Use a custom HTTP method |
| `-H`, `--header HEADER` | Add a request header; may be repeated |
| `-d`, `--data DATA` | Send a raw request body |
| `-F`, `--form FORM` | Send form data or upload a file; may be repeated |
| `-I`, `--head` | Send a HEAD request |
| `-u`, `--user USER:PASS` | Use basic authentication |
| `-b`, `--cookie COOKIE` | Send cookies |
| `-c`, `--cookie-jar FILE` | Save response cookies |
| `--max-time SECONDS` | Set timeout; decimal values are supported |
| `-L`, `--location` | Follow redirects |
| `-k`, `--insecure` | Disable TLS certificate verification |
| `-v`, `--verbose` | Show request and response details |
| `-A`, `--user-agent VALUE` | Set a custom User-Agent |
| `-o`, `--output FILE` | Save raw response bytes to a file |
| `--version` | Display the MyCurl version |
| `--help` | Display help |

---

## Examples

### Custom method

```powershell
python main.py -X DELETE https://example.com/resource/10
```

### Custom headers

```powershell
python main.py `
  -H "Accept: application/json" `
  -H "X-Test: hello" `
  https://example.com
```

### POST data

When `-d` is used without `-X`, MyCurl selects `POST` automatically.

```powershell
python main.py -d "name=Reo&role=developer" https://example.com/form
```

### JSON request

```powershell
python main.py `
  -X POST `
  -H "Content-Type: application/json" `
  -d '{"name":"Reo","role":"developer"}' `
  https://example.com/api
```

### Form data

```powershell
python main.py `
  -F "name=Reo" `
  -F "role=developer" `
  https://example.com/form
```

### File upload

```powershell
python main.py `
  -F "description=Example upload" `
  -F "file=@example.txt" `
  https://example.com/upload
```

### Basic authentication

```powershell
python main.py -u "username:password" https://example.com/private
```

Passwords may contain additional colons because MyCurl splits authentication
only on the first colon.

### Send cookies

```powershell
python main.py `
  -b "session=abc123; theme=dark" `
  https://example.com
```

### Save response cookies

```powershell
python main.py -c cookies.txt https://example.com
```

### Follow redirects

```powershell
python main.py -L https://example.com/redirect
```

### Decimal timeout

```powershell
python main.py --max-time 5.5 https://example.com
```

### Ignore TLS verification

```powershell
python main.py -k https://self-signed.badssl.com
```

Use `-k` only when certificate verification is intentionally being bypassed.

### Verbose output

```powershell
python main.py -v https://example.com
```

Verbose mode includes:

- outgoing method and path;
- Host;
- prepared request headers;
- request body when present;
- response status;
- response headers;
- response body;
- elapsed time;
- response size.

### HEAD request

```powershell
python main.py -I https://example.com
```

### Save a binary response

```powershell
python main.py `
  -o image.png `
  https://httpbingo.org/image/png
```

MyCurl writes the raw response bytes, so images, archives, PDFs, and other
binary files are preserved correctly.

### Custom User-Agent

```powershell
python main.py `
  -A "CustomAgent/1.0" `
  https://example.com
```

The default User-Agent is:

```text
MyCurl/2.1
```

---

## Default method behavior

When `-X` is not supplied:

| Input | Selected method |
|---|---|
| URL only | `GET` |
| `-d DATA` | `POST` |
| `-F FORM` | `POST` |

An explicit `-X` value always takes priority.

---

## Error handling

MyCurl converts expected failures into readable command-line errors.

Example:

```text
mycurl: Invalid URL: example.com
```

Handled error categories include:

- invalid URL;
- unsupported method;
- malformed header;
- invalid timeout;
- malformed authentication;
- malformed form data;
- malformed cookie data;
- missing upload file;
- output-file failure;
- cookie-file failure;
- request timeout;
- excessive redirects;
- TLS certificate failure;
- connection failure;
- unexpected Requests failure.

Handled failures exit with a non-zero process status.

---

## Project structure

```text
MyCurl/
├── .gitignore
├── main.py
├── README.md
├── PROJECT_DOCUMENTATION.md
├── requirements.txt
│
├── cli/
│   ├── README.md
│   ├── parser.py
│   └── validator.py
│
├── core/
│   ├── README.md
│   ├── client.py
│   ├── methods.py
│   ├── request.py
│   └── response.py
│
├── output/
│   ├── README.md
│   ├── formatter.py
│   └── printer.py
│
├── tests/
│   ├── README.md
│   ├── test_cli.py
│   ├── test_client.py
│   ├── test_formatter.py
│   ├── test_helpers.py
│   ├── test_main.py
│   ├── test_parser.py
│   ├── test_printer.py
│   ├── test_request.py
│   ├── test_response.py
│   └── test_validator.py
│
└── utils/
    ├── README.md
    ├── errors.py
    └── helpers.py
```

---

## Architecture

A request moves through the project in this order:

```text
Terminal command
      |
      v
cli/parser.py
Parses command-line arguments
      |
      v
main.py
Selects defaults and coordinates the application
      |
      v
cli/validator.py
Validates user input
      |
      v
utils/helpers.py
Parses headers, auth, cookies, forms, and files
      |
      v
core/request.py
Stores outgoing request settings
      |
      v
core/client.py
Sends the HTTP request
      |
      v
core/response.py
Wraps response data
      |
      v
output/formatter.py
Creates terminal output
      |
      v
output/printer.py
Prints text or saves raw bytes
```

### Directory responsibilities

| Directory | Responsibility |
|---|---|
| `cli/` | Command-line parsing and validation |
| `core/` | Request model, networking, response model, and HTTP methods |
| `output/` | Terminal formatting and binary-safe file output |
| `utils/` | Parsing helpers, cookie writing, file cleanup, and exceptions |
| `tests/` | Unit, mocked integration, direct-main, and subprocess tests |

For deeper technical details, see:

```text
PROJECT_DOCUMENTATION.md
cli/README.md
core/README.md
output/README.md
utils/README.md
tests/README.md
```

---

## Testing

Run all tests:

```powershell
python -m pytest -v
```

Current result:

```text
109 passed
```

Run the coverage report:

```powershell
python -m pytest --cov=. --cov-report=term-missing
```

Current result:

```text
100% total coverage
0 missed statements
```

### Test coverage

The test suite covers:

- CLI parsing;
- URL, method, header, timeout, auth, and form validation;
- header, authentication, cookie, and form parsing;
- cookie-file output;
- multi-upload cleanup;
- request-model behavior;
- response-model getters and calculations;
- HTTP client option forwarding;
- default and custom headers;
- timeout, redirect, TLS, connection, and fallback errors;
- JSON, verbose, normal, and HEAD formatting;
- binary-safe output;
- output-file failures;
- main coordinator behavior;
- process exit codes;
- real CLI help and version behavior.

### Test files

| Test file | Main responsibility |
|---|---|
| `test_cli.py` | End-to-end CLI subprocess behavior |
| `test_client.py` | Mocked networking behavior |
| `test_formatter.py` | Response formatting |
| `test_helpers.py` | Parsing, cookie writing, and cleanup |
| `test_main.py` | Direct `main()` orchestration and exception handling |
| `test_parser.py` | Argparse configuration |
| `test_printer.py` | Terminal and binary file output |
| `test_request.py` | Request model |
| `test_response.py` | Response model |
| `test_validator.py` | Input validation |

---

## Development status

MyCurl 2.1 is feature-complete for its current HTTP and HTTPS scope.

Current quality status:

```text
109 automated tests
109 passing tests
100% measured statement coverage
0 missed statements
```

The project includes unit tests, mocked client tests, direct coordinator tests,
and subprocess-level CLI tests.

---

## Current limitations

MyCurl intentionally focuses on common HTTP and HTTPS workflows. It does not
attempt to reproduce every cURL feature.

Current limitations include:

- verbose output is not yet separated to stderr;
- displayed protocol text is currently fixed as `HTTP/1.1`;
- large responses are loaded into memory instead of streamed;
- protocols such as FTP are not supported;
- advanced cURL options are outside the current project scope.

---

## Possible future improvements

- GitHub Actions continuous integration
- Installable package metadata
- A direct `mycurl` console command
- Separate verbose output to stderr
- Streaming for large responses
- Actual HTTP protocol-version detection
- More cURL-compatible output and data options
- Additional supported protocols

---

## Quick verification

```powershell
python -m pytest
python -m pytest --cov=. --cov-report=term-missing
python main.py --version
```

Expected:

```text
109 passed
100% coverage
MyCurl 2.1
```
