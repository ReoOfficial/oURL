# MyCurl

MyCurl is a lightweight, cURL-inspired command-line HTTP client written in Python.

The project recreates commonly used cURL functionality while demonstrating command-line interface design, HTTP communication, input validation, error handling, file uploads, cookies, authentication, and separation of responsibilities.

> MyCurl is an independent educational project and is not affiliated with the official cURL project.

## Features

* Send HTTP and HTTPS requests
* Support for `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, and `OPTIONS`
* Custom HTTP methods with `-X`
* Custom and repeated request headers with `-H`
* Request bodies with `-d`
* Multipart form data and file uploads with `-F`
* HTTP Basic Authentication with `-u`
* Request and response cookies
* Cookie-jar file saving
* Custom User-Agent headers
* Redirect following with `-L`
* Configurable request timeouts
* Optional TLS certificate verification
* Verbose request and response information
* Request timing and response-size information
* JSON response pretty-printing
* Response output files
* Structured validation and custom exceptions

## Requirements

* Python 3
* pip
* Dependencies listed in `requirements.txt`

## Installation

Clone the repository:

```bash
git clone https://github.com/ReoOfficial/oURL.git
cd oURL
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```text
mycurl [options] URL
```

While running the project directly from source:

```bash
python main.py [options] URL
```

Display all available options:

```bash
python main.py --help
```

## Examples

### Basic GET request

```bash
python main.py https://postman-echo.com/get
```

### Verbose request

```bash
python main.py -v https://postman-echo.com/get
```

Verbose mode displays the outgoing request, incoming response headers, request duration, and response size.

### POST form-encoded data

```bash
python main.py -d "name=Reo" https://postman-echo.com/post
```

Using `-d` automatically selects `POST` unless a method is explicitly supplied with `-X`.

### Send JSON

```bash
python main.py \
  -H "Content-Type: application/json" \
  -d '{"name":"Reo"}' \
  https://postman-echo.com/post
```

### Custom request method

```bash
python main.py -X DELETE https://postman-echo.com/delete
```

### Multiple headers

```bash
python main.py \
  -H "Accept: application/json" \
  -H "X-Project: MyCurl" \
  https://postman-echo.com/get
```

### Multipart form data

```bash
python main.py \
  -F "name=Reo" \
  -F "role=developer" \
  https://postman-echo.com/post
```

### File upload

```bash
python main.py \
  -F "file=@example.txt" \
  https://postman-echo.com/post
```

### Basic Authentication

```bash
python main.py \
  -u "username:password" \
  https://postman-echo.com/basic-auth
```

### Send cookies

```bash
python main.py \
  -b "session=abc123; theme=dark" \
  https://postman-echo.com/get
```

### Save response cookies

```bash
python main.py \
  -c cookies.txt \
  https://postman-echo.com/cookies/set?session=abc123
```

### Follow redirects

```bash
python main.py -L https://example.com
```

### Save the response

```bash
python main.py \
  -o response.txt \
  https://postman-echo.com/get
```

### Set a timeout

```bash
python main.py \
  --max-time 5 \
  https://postman-echo.com/get
```

### Disable certificate verification

```bash
python main.py -k https://example.com
```

Disabling certificate verification should only be used for development or testing.

## Project Structure

```text
MyCurl/
├── main.py
├── README.md
├── requirements.txt
│
├── cli/
│   ├── parser.py
│   └── validator.py
│
├── core/
│   ├── client.py
│   ├── methods.py
│   ├── request.py
│   └── response.py
│
├── output/
│   ├── formatter.py
│   └── printer.py
│
└── utils/
    ├── errors.py
    └── helpers.py
```

### Responsibilities

* `main.py` coordinates argument parsing, validation, requests, and output.
* `cli/parser.py` defines the command-line interface.
* `cli/validator.py` validates user input.
* `core/request.py` represents an outgoing request.
* `core/client.py` sends requests through the Requests library.
* `core/response.py` represents received responses.
* `output/formatter.py` formats normal and verbose output.
* `output/printer.py` prints responses or writes them to files.
* `utils/helpers.py` parses headers, authentication, cookies, and forms.
* `utils/errors.py` contains custom exceptions.

## Error Handling

MyCurl provides readable errors for situations including:

* Invalid URLs
* Unsupported HTTP methods
* Invalid header formats
* Invalid timeout values
* Connection failures
* Request timeouts
* Missing upload files

Example:

```text
mycurl: Invalid header format: WrongHeader
Expected: Key: Value
```

## Project Status

The primary HTTP functionality is implemented.

The next development milestone is an automated test suite covering:

* Argument parsing
* Header parsing
* URL and method validation
* Cookie parsing
* Form parsing
* File-upload errors
* Response formatting
* Timeout and connection handling

## Testing

MyCurl includes 56 automated tests covering:

* Command-line argument parsing
* URL, HTTP method, header, and timeout validation
* Header, authentication, cookie, and form parsing
* Request configuration and method selection
* HEAD request behavior
* Default and custom request headers
* Response formatting
* Verbose output
* Timing and response-size output
* Timeout and connection-error handling
* Uploaded-file cleanup

Run the complete test suite:

```bash
python -m pytest -v
```

Run the tests with coverage:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

Current test results:

```text
56 passed
85% total coverage
```

## Current Limitations

* The project currently focuses on HTTP and HTTPS.
* It does not support every protocol or option available in the official cURL tool.
* Binary download handling and shell installation are still areas for future improvement.

## Future Improvements

* Automated tests with pytest
* Continuous integration with GitHub Actions
* Binary-safe response output
* Standard output and standard error separation
* Installable command-line package
* Additional cURL-compatible options
