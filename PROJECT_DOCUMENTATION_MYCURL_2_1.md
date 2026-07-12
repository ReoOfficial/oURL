# MyCurl 2.1 — Technical Documentation

**Repository:** `ReoOfficial/oURL`  
**Language:** Python  
**Purpose:** A lightweight, cURL-inspired command-line HTTP client  
**Last reviewed:** July 12, 2026

---

## 1. Project overview

MyCurl is a command-line program that sends HTTP and HTTPS requests. A user provides a URL and optional flags such as `-X`, `-H`, `-d`, `-F`, `-v`, or `-I`. The program parses those arguments, validates them, converts them into Python values, sends the request through the `requests` library, wraps the result in a custom `Response` object, formats the output, and either prints formatted text or writes raw response bytes to a file.

A simple request looks like this:

```powershell
python main.py https://example.com
```

A verbose POST request looks like this:

```powershell
python main.py -v -d "name=Reo" https://postman-echo.com/post
```

### One-sentence explanation

> MyCurl is a modular Python CLI that parses and validates cURL-like options, builds an HTTP request, sends it through the Requests library, wraps the response, and formats the result for the terminal or a file.

---

## 2. Architecture and request flow

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
Selects the default method and coordinates the program
      |
      v
cli/validator.py
Rejects invalid URLs, methods, headers, timeouts, auth, or forms
      |
      v
utils/helpers.py
Converts strings into headers, auth tuples, cookies, form fields, and files
      |
      v
core/request.py
Stores the complete request configuration
      |
      v
core/client.py
Sends the HTTP request using requests.request(...)
      |
      v
core/response.py
Stores response data behind a stable project-specific interface
      |
      v
output/formatter.py
Creates normal, verbose, or HEAD output
      |
      v
output/printer.py
Prints formatted text or writes raw response bytes to a file
```

### Example flow

For this command:

```powershell
python main.py -v -d "name=Reo" https://postman-echo.com/post
```

1. `parser.py` recognizes the URL, `-v`, and `-d`.
2. `main.py` sees request data and chooses `POST` because no explicit `-X` method was provided.
3. `validator.py` checks the URL, method, timeout, and other arguments.
4. `helpers.py` parses headers, cookies, authentication, and forms.
5. `main.py` creates a `Request` object.
6. `client.py` adds the default User-Agent and form content type, then calls `requests.request`.
7. `client.py` wraps the external Requests response in the project's `Response` class.
8. `formatter.py` creates cURL-like verbose output and adds timing and size.
9. `printer.py` prints the final string or saves raw response bytes when `-o` is used.

### Project structure

```text
MyCurl/
├── .gitignore
├── main.py
├── README.md
├── PROJECT_DOCUMENTATION.md
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
├── tests/
│   ├── test_cli.py
│   ├── test_client.py
│   ├── test_formatter.py
│   ├── test_helpers.py
│   ├── test_parser.py
│   ├── test_printer.py
│   └── test_validator.py
│
└── utils/
    ├── errors.py
    └── helpers.py
```

---

# 3. Root files

## `main.py`

### Purpose

`main.py` is the application's entry point and coordinator. It connects all other modules but avoids implementing their internal details itself.

### Main responsibilities

- Calls `parse_args()` to read the command line.
- Selects a default HTTP method:
  - `POST` when `-d` or `-F` is present.
  - `GET` otherwise.
- Calls `validate(args)` before sending anything.
- Parses forms, headers, authentication, and cookies.
- Creates the custom `Request` object.
- Creates a `Client` and sends the request.
- Saves received cookies when `-c` is supplied.
- Formats and prints or saves the response.
- Converts custom exceptions into readable CLI errors and exit codes.

### Important logic

```python
if args.method is None:
    if args.data or args.form:
        args.method = "POST"
    else:
        args.method = "GET"
```

This reproduces an important cURL-like behavior: sending data implies `POST` unless the user explicitly chooses another method with `-X`.

### Dependencies

`main.py` imports functionality from every main project layer:

- `cli.parser`
- `cli.validator`
- `core.request`
- `core.client`
- `output.formatter`
- `output.printer`
- `utils.helpers`
- `utils.errors`

### Input and output

**Input:** command-line arguments from the user.  
**Output:** terminal text, an output file, a cookie file, or a readable error.

### Why this file exists

Without `main.py`, the modules would be separate pieces with no execution flow. Its job is orchestration, not low-level networking or formatting.


### Error behavior

Handled application errors print a readable `mycurl:` message and exit with a non-zero process status. This includes validation failures, TLS errors, redirect loops, file-write failures, connection failures, and unexpected Requests-level errors.

---

## `README.md`

### Purpose

The README is the public introduction and user guide shown on the repository's GitHub page.

### Main responsibilities

- Explains what MyCurl is.
- Lists implemented features.
- Provides installation instructions.
- Shows command examples.
- Documents the project structure.
- Explains error handling.
- Describes tests, coverage, limitations, and future work.

### Intended audience

- A developer evaluating the repository.
- A colleague trying to install or use the CLI.
- A recruiter or manager reviewing the project.
- The project's future maintainer.

### Relationship to this document

The README explains **how to install and use** MyCurl. This document explains **how the code works internally**.

### Current state

The README should identify the current release as MyCurl 2.1 and report 82 automated tests, 87% measured coverage, binary-safe downloads, decimal timeouts, hardened error handling, and end-to-end CLI tests.

---

## `PROJECT_DOCUMENTATION.md`

### Purpose

This file provides internal technical documentation for the project.

### Main responsibilities

- Explains the architecture and request flow.
- Documents the purpose of every source file.
- Describes the behavior of each major function and class.
- Documents the test suite and coverage.
- Records current limitations and future improvement areas.

---

## `requirements.txt`

### Purpose

`requirements.txt` records the Python packages needed to install and test the project consistently.

### Main dependencies

- `requests`: sends HTTP and HTTPS requests.
- `certifi`: provides a trusted certificate-authority bundle.
- `charset-normalizer`: helps Requests determine text encodings.
- `idna`: supports internationalized domain names.
- `urllib3`: provides lower-level HTTP connection functionality used by Requests.
- `pytest`: runs the automated test suite.
- `pytest-cov`: measures test coverage.

### Usage

```powershell
python -m pip install -r requirements.txt
```

### Why versions are pinned

Pinned versions make installations reproducible. A colleague installing the project receives the same dependency versions that were used during development and testing.

---

## `.gitignore`

### Purpose

`.gitignore` tells Git which generated, temporary, or local files should not be committed.

### Ignored content

- `__pycache__/` and `*.pyc`: compiled Python cache files.
- `.pytest_cache/`: pytest's local cache.
- `.coverage` and `htmlcov/`: generated coverage data.
- `.venv/` and `venv/`: local virtual environments.
- `response.txt`: example output generated by `-o`.
- `cookies.txt`: example cookie-jar output.

### Why this matters

These files are machine-specific or generated automatically. Keeping them out of Git makes the repository cleaner and prevents unnecessary changes.

---

# 4. CLI layer

## `cli/parser.py`

### Purpose

`parser.py` defines the command-line interface with Python's `argparse` module.

### Main function

```python
parse_args()
```

It creates an `ArgumentParser`, registers every supported option, and returns a namespace containing the parsed values.

### Supported arguments

#### Target

- `URL`: required target URL.

#### Request options

- `-X`, `--request`: explicitly sets the HTTP method.
- `-H`, `--header`: adds a request header; can be repeated.
- `-d`, `--data`: supplies a request body.
- `-F`, `--form`: adds form data or a file upload; can be repeated.
- `-I`, `--head`: requests headers using the HEAD method.

#### Authentication and cookies

- `-u`, `--user`: accepts `username:password`.
- `-b`, `--cookie`: sends cookies.
- `-c`, `--cookie-jar`: saves received cookies.

#### Connection options

- `--max-time`: sets the request timeout in seconds and accepts decimal values such as `5.5`.
- `-L`, `--location`: follows redirects.
- `-k`, `--insecure`: disables TLS certificate verification.

#### Output options

- `-v`, `--verbose`: displays request and response details.
- `-A`, `--user-agent`: overrides the default User-Agent.
- `-o`, `--output`: writes raw response bytes to a file.

#### Metadata

- `--version`: prints `MyCurl 2.1`.
- `--help`: generated automatically by argparse.

### Important `argparse` concepts used

- `action="append"` allows repeated `-H` and `-F` options.
- `action="store_true"` converts flags such as `-v` into booleans.
- `type=float` allows decimal timeout values.
- `metavar` improves how values appear in help output.
- argument groups make `--help` easier to read.
- `RawTextHelpFormatter` preserves the formatting of command examples.

### Input and output

**Input:** values from `sys.argv`.  
**Output:** an `argparse.Namespace` used by `main.py`.


---

## `cli/validator.py`

### Purpose

`validator.py` checks whether parsed command-line values are acceptable before networking or file handling begins.

### Public functions

#### `validate(args)`

Runs every individual validation function and returns the original argument namespace when all checks pass.

#### `validate_url(url)`

Uses `urlparse` and requires:

- scheme to be `http` or `https`;
- a non-empty network location, such as `example.com`.

Invalid input raises `InvalidURLException`.

#### `validate_method(method)`

- Allows `None`, because `main.py` may select the default method.
- Converts the method to uppercase for comparison.
- Checks it against `SUPPORTED_METHODS`.

Invalid input raises `InvalidMethodException`.

#### `validate_headers(headers)`

Checks every `-H` value:

- it must contain `:`;
- the header name before `:` cannot be empty.

Invalid input raises `InvalidHeaderException`.

#### `validate_timeout(timeout)`

Requires a timeout greater than zero.

Invalid input raises `InvalidTimeoutException`.

#### `validate_auth(auth)`

When authentication is supplied:

- it must contain `:`;
- the username before the first `:` cannot be empty.

Invalid input raises `InvalidAuthException`.

#### `validate_forms(forms)`

Every form entry:

- must contain `=`;
- must have a non-empty field name.

Invalid input raises `InvalidFormException`.

### Why validation is separate from parsing

Parsing determines the shape and type of CLI values. Validation determines whether those values make sense for this application.

For example, argparse converts `--max-time 5.5` into a floating-point number, while the validator rejects `--max-time 0`.


---

# 5. Core layer

## `core/methods.py`

### Purpose

This file defines the HTTP methods officially supported by MyCurl.

```python
SUPPORTED_METHODS = (
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
)
```

### Why this is a separate file

It gives the project one source of truth. The validator does not need to hardcode the methods itself, and adding a supported method only requires changing this tuple.

### Used by

`cli/validator.py` imports `SUPPORTED_METHODS` to approve or reject `-X` values.

---

## `core/request.py`

### Purpose

`request.py` defines the project's internal `Request` data object.

### Main class

```python
Request
```

The constructor receives all settings needed to send and format a request.

### Stored attributes

- `method`: HTTP method.
- `url`: destination URL.
- `headers`: parsed header dictionary.
- `body`: raw `-d` request data.
- `timeout`: maximum request duration.
- `verbose`: whether verbose output is enabled.
- `follow_redirects`: controls redirect following.
- `insecure`: controls TLS verification.
- `auth`: authentication tuple.
- `user_agent`: optional custom User-Agent.
- `output`: optional output filename.
- `head`: whether `-I` was requested.
- `cookies`: parsed cookies.
- `cookie_jar`: optional cookie output filename.
- `form_data`: normal form fields.
- `form_files`: opened upload files.

### Default handling

Mutable values are protected with patterns such as:

```python
self.headers = headers or {}
self.form_files = form_files or {}
```

This avoids sharing one mutable default dictionary between different objects.

### Why use a class

A request has many related settings. Passing fifteen separate parameters through every function would be hard to read and easy to misuse. A single object keeps the configuration together.

### Used by

- Created in `main.py`.
- Read by `core/client.py`.
- Read by `output/formatter.py`.


---

## `core/client.py`

### Purpose

`client.py` is the networking layer. It converts the internal `Request` object into an actual HTTP request through the external `requests` library.

### Main class and method

```python
Client.send(request)
```

### Step-by-step behavior

1. Copies custom headers so the original request dictionary is not modified directly.
2. Sets the User-Agent:
   - custom value from `-A`, or
   - default `MyCurl/2.1`.
3. Adds `Content-Type: application/x-www-form-urlencoded` when:
   - a body exists;
   - the request is not using multipart form data;
   - the user did not provide a Content-Type.
4. Reads authentication from the request.
5. Changes the actual method to `HEAD` when `request.head` is true.
6. Calls `requests.request(...)`.
7. Passes all networking options:
   - method;
   - URL;
   - headers;
   - data;
   - files;
   - timeout;
   - TLS verification;
   - redirects;
   - authentication;
   - cookies.
8. Wraps the returned Requests response in `core.response.Response`.
9. Stores `response.request.headers`, which are the prepared headers actually used by Requests.
10. Converts Requests failures into project-specific exceptions.
11. Distinguishes timeouts, excessive redirects, TLS failures, connection failures, and unexpected Requests errors.
12. Closes every opened upload file in a `finally` block.

### Form and body behavior

```python
data=request.form_data if request.form_data else request.body
```

Form fields take priority over the raw body. Multipart files are passed separately through `files=request.form_files`.

### Why prepared headers matter

Requests can generate headers automatically, including:

- `Content-Length`;
- multipart `Content-Type` boundaries;
- encoding-related headers.

Saving `response.request.headers` lets verbose mode display what was actually prepared, not only what the user typed.

### Error translation

- `requests.exceptions.Timeout` becomes `RequestTimeoutException`.
- `requests.exceptions.TooManyRedirects` becomes `TooManyRedirectsException`.
- `requests.exceptions.SSLError` becomes `TLSException`.
- `requests.exceptions.ConnectionError` becomes `ConnectionException`.
- Any other `requests.exceptions.RequestException` becomes `RequestFailedException`.

Specific exceptions are caught before broader parent exceptions. This prevents Requests-specific tracebacks from leaking through the application's public interface.

### Resource cleanup

The `finally` block closes uploaded files whether the request succeeds or fails. In addition, `parse_forms()` closes already opened files if a later file fails during form parsing.


---

## `core/response.py`

### Purpose

`response.py` wraps the third-party Requests response in a project-specific object.

### Main class

```python
Response
```

### Stored response data

- `status_code`: numeric HTTP status.
- `reason`: text such as `OK` or `Not Found`.
- `headers`: response headers.
- `body`: decoded text body.
- `content`: raw body bytes.
- `url`: final response URL.
- `elapsed`: Requests timing object.
- `cookies`: received cookies.
- `history`: redirect responses.
- `sent_headers`: prepared outgoing request headers.

### Getter methods

The class exposes getters such as:

- `get_status_code()`
- `get_headers()`
- `get_body()`
- `get_content()`
- `get_reason()`
- `get_url()`
- `get_elapsed()`
- `get_cookies()`
- `get_history()`
- `get_sent_headers()`

### Calculated methods

#### `get_elapsed_seconds()`

Converts the Requests `timedelta` into a floating-point number of seconds.

#### `get_size()`

Returns the number of received body bytes:

```python
len(self.content)
```

Using bytes is more accurate than counting decoded text characters.

### Why use a wrapper

The rest of the project depends on the project's own stable interface instead of directly depending on every detail of `requests.Response`.

It also provides a natural place for project-specific calculations such as elapsed seconds and response size.

### Maintenance note

If legacy methods such as `get_form_data()` or `get_form_files()` remain without matching attributes, they should be removed or implemented before being used.

---

# 6. Output layer

## `output/formatter.py`

### Purpose

`formatter.py` converts a `Request` and `Response` into the string shown to the user.

### Functions

#### `format_body(body)`

Attempts to parse the response body as JSON.

- Valid JSON is printed with indentation.
- Non-JSON text is returned unchanged.
- Unicode characters are preserved with `ensure_ascii=False`.

Example:

```json
{"message":"hello"}
```

becomes:

```json
{
    "message": "hello"
}
```

#### `format_response(request, response)`

Builds the final output based on the selected mode.

### Normal mode

For a normal request, it prints only the formatted response body.

### Verbose mode

Verbose output includes:

- outgoing method and path;
- Host;
- outgoing prepared request headers;
- outgoing request body when present;
- incoming HTTP status;
- response headers;
- response body, except for HEAD;
- elapsed time;
- response size.

The `>` prefix represents sent request information.  
The `<` prefix represents received response information.

### HEAD mode

When `-I` is used without `-v`, the formatter prints:

- status line;
- response headers;
- no response body.

When `-I` and `-v` are combined, it displays `HEAD` as the outgoing method even if the internal default method originally began as GET.

### URL handling

`urlparse` separates the URL into components so verbose mode can display only the request path and query:

```text
/test?name=Reo
```

instead of the full URL.

### Current technical notes

- The displayed protocol is hardcoded as `HTTP/1.1`; the actual connection might use another HTTP version.
- Verbose information is still assembled as formatted terminal text. A future improvement would separate verbose information to stderr and the response body to stdout more closely to real cURL.

---

## `output/printer.py`

### Purpose

`printer.py` decides where the already formatted output goes.

### Main function

```python
print_response(output, filename=None, content=None)
```

### Behavior

When `filename` is provided:

1. opens the file in binary mode;
2. writes the raw `response.content` bytes;
3. prints a confirmation message.

Without a filename, it prints formatted text to the terminal.

File-system failures are converted into `FileWriteException`, so invalid or forbidden paths fail cleanly without a raw traceback.

### Why formatting and printing are separate

The formatter decides **what the output looks like**. The printer decides **where the output goes**. This separation makes formatter tests possible without writing files or capturing the terminal.

### Binary-safe output

Using binary mode preserves images, archives, PDFs, and other non-text responses exactly as received.

---

# 7. Utility layer

## `utils/helpers.py`

### Purpose

`helpers.py` converts raw command-line strings into structures used by the core layer and handles cookie-file output.

### Functions

#### `parse_headers(headers)`

Converts:

```python
["Accept: application/json", "X-Test: value"]
```

into:

```python
{
    "Accept": "application/json",
    "X-Test": "value",
}
```

It splits only on the first colon, so a header value may contain additional colons.

#### `parse_auth(auth)`

Converts:

```text
username:password
```

into:

```python
("username", "password")
```

It also splits only once, allowing a password to contain colons.

#### `parse_cookies(cookie)`

Validates and converts a semicolon-separated cookie string into a dictionary. Each cookie must use `name=value`, and the cookie name cannot be empty. Invalid values raise `InvalidCookieException`.

Example:

```text
session=abc123; theme=dark
```

becomes:

```python
{
    "session": "abc123",
    "theme": "dark",
}
```

#### `parse_forms(forms)`

Separates normal form fields from file uploads.

Normal value:

```text
name=Reo
```

becomes an entry in the `data` dictionary.

File value:

```text
file=@example.txt
```

opens `example.txt` in binary mode and stores the file object in the `files` dictionary.

Missing or unreadable files raise `FileUploadException`. If one upload opens and a later upload fails, every previously opened file is closed before the exception is re-raised.

#### `save_cookies(cookies, filename)`

Writes received cookies in Netscape cookie-file format. File-system failures raise `FileWriteException`. It stores:

- domain;
- subdomain flag;
- path;
- secure flag;
- expiration;
- cookie name;
- cookie value.

### Why these functions are separate

They keep string parsing and file-format logic out of `main.py` and `Client.send()`. They can also be tested independently.


---

## `utils/errors.py`

### Purpose

This module defines custom exception types for errors that MyCurl understands.

### Exception classes

- `InvalidURLException`
- `InvalidMethodException`
- `InvalidHeaderException`
- `InvalidTimeoutException`
- `InvalidAuthException`
- `InvalidFormException`
- `InvalidCookieException`
- `RequestTimeoutException`
- `TooManyRedirectsException`
- `TLSException`
- `ConnectionException`
- `RequestFailedException`
- `FileUploadException`
- `FileWriteException`

### Why empty exception classes are useful

Although each class only contains `pass`, its type identifies the category of failure.

This allows code such as:

```python
except RequestTimeoutException:
    print("mycurl: Request timed out")
```

without checking error-message strings.

### Error flow example

1. Requests raises `requests.exceptions.Timeout`.
2. `Client.send()` catches it.
3. The client raises `RequestTimeoutException`.
4. `main.py` catches the custom exception.
5. The user sees a clean MyCurl error.

---

# 8. Test suite

The project contains 82 automated pytest tests. Most tests are isolated unit tests, the client tests mock networking, and the CLI tests launch the real entry point in subprocesses.

## `tests/test_cli.py`

### Purpose

Tests the complete command-line program through `main.py`.

### Covered behavior

- `--version` and `--help`;
- invalid URLs and headers;
- malformed cookies;
- invalid authentication and forms;
- invalid timeout values;
- nonexistent upload files;
- non-zero process exit codes;
- absence of raw Python tracebacks.

### Test count

9 tests.

### Coverage note

These tests execute `main.py` in child processes. The standard parent-process coverage report does not automatically attribute that execution to `main.py`, even though the entry point is genuinely tested.

---

## `tests/test_client.py`

### Purpose

Tests networking logic without making real network requests.

### Covered behavior

- GET and HEAD method selection;
- default and custom User-Agent values;
- automatic and custom Content-Type values;
- form data priority over a raw body;
- timeout, TLS, redirect, authentication, and cookie options;
- prepared request headers;
- timeout, TLS, connection, excessive redirect, and fallback request errors;
- uploaded-file cleanup.

### Test count

15 tests.

---

## `tests/test_formatter.py`

### Purpose

Tests response-body and terminal-output formatting.

### Covered behavior

- JSON pretty-printing;
- unchanged plain text;
- normal body output;
- verbose request and response details;
- timing and response size;
- POST body display;
- HEAD output without a body;
- correct HEAD method display.

### Test count

8 tests.

---

## `tests/test_helpers.py`

### Purpose

Tests conversion and file-handling functions in `utils/helpers.py`.

### Covered behavior

- single and repeated headers;
- colons inside header values and passwords;
- authentication parsing;
- single and repeated cookies;
- malformed cookies and empty cookie names;
- form data;
- cookie-jar write failures;
- cleanup when a later upload fails after an earlier file opened.

### Test count

14 tests.

---

## `tests/test_parser.py`

### Purpose

Tests the command-line parser without launching a separate process.

### Covered behavior

- URL and default values;
- decimal timeouts;
- custom methods;
- repeated headers and forms;
- request bodies;
- verbose and redirect flags;
- authentication and cookies;
- HEAD and output options.

### Test count

10 tests.

---

## `tests/test_printer.py`

### Purpose

Tests file-output behavior.

### Covered behavior

- invalid output paths raise `FileWriteException`;
- binary response bytes are written exactly without corruption.

### Test count

2 tests.

---

## `tests/test_validator.py`

### Purpose

Tests input validation.

### Covered behavior

- valid and invalid HTTP/HTTPS URLs;
- supported and unsupported methods;
- valid and malformed headers;
- integer and decimal timeouts;
- zero and negative timeouts;
- valid and invalid authentication;
- valid and invalid forms.

### Testing techniques

- `pytest.raises(...)` checks expected exceptions.
- `pytest.mark.parametrize(...)` runs one test with several values.

### Test count

24 tests after parameter expansion.

---

# 9. Generated and ignored folders

## `__pycache__/`

Created automatically by Python to store compiled bytecode. It is not project source code and should not be documented or committed as part of the application.

## `.pytest_cache/`

Created by pytest to remember test information such as previous failures. It is local development data.

## `.coverage`

Generated by coverage.py through pytest-cov. It stores raw coverage measurements.

These files are correctly excluded through `.gitignore`.

---

# 10. Testing and coverage

Run all tests:

```powershell
python -m pytest -v
```

Run the coverage report:

```powershell
python -m pytest --cov=. --cov-report=term-missing
```

Current reported result:

```text
82 passed
87% total coverage
```

### Latest module coverage

```text
cli/parser.py          100%
cli/validator.py        82%
core/client.py         100%
core/methods.py        100%
core/response.py        68%
main.py                  0%*
output/formatter.py     98%
output/printer.py       90%
utils/errors.py        100%
utils/helpers.py        85%
```

`main.py` is marked as 0% by the standard report because the end-to-end CLI tests execute it in subprocesses. Those tests still verify its real output and exit behavior.

High coverage does not prove that no bugs exist. It means the tests executed a large percentage of measured statements. Test quality still depends on whether the assertions cover meaningful behavior.

---

# 11. Reliability improvements in MyCurl 2.1

### Input hardening

- malformed cookies produce `InvalidCookieException`;
- authentication and form validation use dedicated exceptions;
- decimal timeout values are accepted;
- invalid timeout values still fail cleanly.

### Network hardening

- TLS failures are separated from ordinary connection errors;
- excessive redirects produce a readable custom error;
- unexpected Requests-level failures become `RequestFailedException`;
- handled network failures return non-zero exit codes.

### File hardening

- invalid output and cookie-jar paths produce `FileWriteException`;
- binary downloads are saved as raw bytes;
- partially opened upload files are closed if later parsing fails;
- uploaded files are closed after request completion or failure.

### Test hardening

- end-to-end CLI tests verify output and exit codes;
- regression tests cover the newly fixed failures;
- the suite contains 82 tests;
- measured coverage is 87%.

---

# 12. Current limitations and future improvements

MyCurl is complete for its current HTTP/HTTPS project scope, but it is not intended to reproduce every cURL feature or protocol.

Possible future improvements include:

- separating verbose information to stderr and response bodies to stdout;
- detecting and displaying the actual HTTP protocol version;
- adding installable package metadata and a direct `mycurl` command;
- adding GitHub Actions continuous integration;
- adding subprocess-aware coverage configuration;
- supporting streaming and very large downloads;
- adding more cURL-compatible data and output options;
- supporting protocols beyond HTTP and HTTPS.

---

# 13. File responsibility cheat sheet

| File | Main responsibility |
|---|---|
| `main.py` | Coordinates the application and maps errors to CLI output |
| `cli/parser.py` | Defines and parses CLI options |
| `cli/validator.py` | Validates user input |
| `core/methods.py` | Lists supported HTTP methods |
| `core/request.py` | Stores outgoing request settings |
| `core/client.py` | Sends requests, translates network errors, and closes upload files |
| `core/response.py` | Wraps response data, raw content, timing, and size |
| `output/formatter.py` | Builds normal, verbose, and HEAD terminal output |
| `output/printer.py` | Prints formatted text or saves raw bytes |
| `utils/helpers.py` | Parses inputs, manages uploads, and saves cookies |
| `utils/errors.py` | Defines custom application exceptions |
| `tests/test_cli.py` | Tests the complete CLI and exit codes |
| `tests/test_client.py` | Tests request-sending logic with mocks |
| `tests/test_formatter.py` | Tests output formatting |
| `tests/test_helpers.py` | Tests helper parsing and cleanup |
| `tests/test_parser.py` | Tests CLI parsing |
| `tests/test_printer.py` | Tests binary and failed file output |
| `tests/test_validator.py` | Tests validation |
| `README.md` | Public installation and usage guide |
| `PROJECT_DOCUMENTATION.md` | Internal technical documentation |
| `requirements.txt` | Records dependencies |
| `.gitignore` | Excludes generated and local files |

---

## Final mental model

The most important concept to remember is:

> `main.py` coordinates, the CLI layer understands the user, the utility layer converts values, the core layer performs HTTP work, the output layer presents or saves the result, and the tests verify each responsibility independently.
