# MyCurl 2.0 — Technical Documentation

**Repository:** `ReoOfficial/oURL`  
**Language:** Python  
**Purpose:** A lightweight, cURL-inspired command-line HTTP client  
**Last reviewed:** July 11, 2026

---

## 1. Project overview

MyCurl is a command-line program that sends HTTP and HTTPS requests. A user provides a URL and optional flags such as `-X`, `-H`, `-d`, `-F`, `-v`, or `-I`. The program parses those arguments, validates them, converts them into Python values, sends the request through the `requests` library, wraps the result in a custom `Response` object, formats the output, and either prints it or writes it to a file.

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
Prints the result or writes it to a file
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
9. `printer.py` prints the final string or saves it when `-o` is used.

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


### Current technical note

The `ConnectionException` handler prints an error but currently does not call `sys.exit(1)`. That means a connection failure may finish with a successful process exit code even though the request failed.

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

### Current technical note

The project-status text says the next milestone is an automated test suite, although the repository now contains 56 tests. That sentence can be updated to say the test milestone is complete. The future-improvements section also still lists automated pytest tests even though they already exist.

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

- `--max-time`: sets the request timeout in seconds.
- `-L`, `--location`: follows redirects.
- `-k`, `--insecure`: disables TLS certificate verification.

#### Output options

- `-v`, `--verbose`: displays request and response details.
- `-A`, `--user-agent`: overrides the default User-Agent.
- `-o`, `--output`: writes output to a file.

#### Metadata

- `--version`: prints `MyCurl 2.0`.
- `--help`: generated automatically by argparse.

### Important `argparse` concepts used

- `action="append"` allows repeated `-H` and `-F` options.
- `action="store_true"` converts flags such as `-v` into booleans.
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

When authentication is supplied, it must contain `:` so it can be separated into username and password.

#### `validate_forms(forms)`

Every form entry must contain `=` so it can be separated into a field name and value.

### Why validation is separate from parsing

Parsing determines the shape and type of CLI values. Validation determines whether those values make sense for this application.

For example, argparse converts `--max-time 5` into an integer, while the validator rejects `--max-time 0`.

### Current technical notes

- Authentication and form errors currently reuse `InvalidHeaderException`. Dedicated `InvalidAuthException` and `InvalidFormException` classes would make error categories clearer.
- The form error message concatenates two strings without a newline or space between them.

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
   - default `MyCurl/2.0`.
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
10. Converts Requests timeout and connection errors into project-specific exceptions.
11. Closes every opened upload file in a `finally` block.

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
- `requests.exceptions.ConnectionError` becomes `ConnectionException`.

This prevents Requests-specific exception details from leaking through the application's public interface.

### Resource cleanup

The `finally` block closes uploaded files whether the request succeeds or fails. This avoids leaking open file handles.


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

### Current technical note

`get_form_data()` and `get_form_files()` refer to `self.form_data` and `self.form_files`, but those attributes are never assigned in the constructor. Calling either method currently raises `AttributeError`. They are also not needed for received HTTP responses and could be removed unless response-side form metadata is added.

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
- Verbose data, response body, time, and size are all combined into one string. Therefore `-o` currently writes all of them to the file when verbose mode is active. Real cURL normally separates verbose information to stderr and the response body to stdout.

---

## `output/printer.py`

### Purpose

`printer.py` decides where the already formatted output goes.

### Main function

```python
print_response(output, filename)
```

### Behavior

When `filename` is provided:

1. opens the file in text write mode with UTF-8;
2. writes the output;
3. prints a confirmation message.

Without a filename, it prints the output to the terminal.

### Why formatting and printing are separate

The formatter decides **what the output looks like**. The printer decides **where the output goes**. This separation makes formatter tests possible without writing files or capturing the terminal.

### Current limitation

The function is text-oriented. Binary downloads such as images, archives, and executables require byte-based handling rather than UTF-8 text output.

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

Converts a semicolon-separated cookie string into a dictionary.

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

Missing files raise `FileUploadException`.

#### `save_cookies(cookies, filename)`

Writes received cookies in Netscape cookie-file format. It stores:

- domain;
- subdomain flag;
- path;
- secure flag;
- expiration;
- cookie name;
- cookie value.

### Why these functions are separate

They keep string parsing and file-format logic out of `main.py` and `Client.send()`. They can also be tested independently.

### Current technical notes

- `parse_cookies()` assumes every cookie pair contains `=`. A malformed cookie can raise a normal `ValueError` instead of a custom exception.
- `save_cookies()` is currently not covered by the main helper tests.

---

## `utils/errors.py`

### Purpose

This module defines custom exception types for errors that MyCurl understands.

### Exception classes

- `InvalidURLException`
- `InvalidMethodException`
- `InvalidHeaderException`
- `InvalidTimeoutException`
- `RequestTimeoutException`
- `ConnectionException`
- `FileUploadException`

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

The project contains 56 automated pytest tests. Most tests are isolated unit tests, and the client tests mock networking so they do not rely on internet access.

## `tests/test_validator.py`

### Purpose

Tests input validation.

### Covered behavior

- valid HTTP/HTTPS URLs;
- empty or malformed URLs;
- unsupported schemes such as FTP;
- valid uppercase and lowercase methods;
- no explicit custom method;
- unsupported methods;
- valid single and repeated headers;
- missing header colon;
- empty header name;
- positive timeout;
- zero and negative timeouts.

### Testing techniques

- `pytest.raises(...)` checks expected exceptions.
- `pytest.mark.parametrize(...)` runs one test with several invalid values.

### Test count

17 tests after parameter expansion.

---

## `tests/test_helpers.py`

### Purpose

Tests conversion functions in `utils/helpers.py`.

### Covered behavior

- single header parsing;
- repeated headers;
- colons inside header values;
- authentication parsing;
- colons inside passwords;
- absent authentication;
- single and repeated cookies;
- absent cookies;
- normal form fields.

### Test count

10 tests.

### Current coverage gap

This file does not currently test:

- file uploads;
- missing upload files;
- cookie-file saving.

---

## `tests/test_parser.py`

### Purpose

Tests the command-line parser without launching a separate process.

### How it works

`monkeypatch` temporarily replaces `sys.argv`, then the test calls `parse_args()` directly.

### Covered behavior

- URL parsing;
- default values;
- custom method;
- repeated headers;
- request body;
- verbose and redirect flags;
- authentication and cookies;
- repeated forms;
- HEAD and output options.

### Test count

9 tests.

### Why this approach is useful

It is fast and checks argparse configuration directly. It avoids starting another Python process for every parser test.

---

## `tests/test_formatter.py`

### Purpose

Tests response-body and terminal-output formatting.

### Test doubles

- `FakeResponse` supplies predictable response values.
- `SimpleNamespace` creates lightweight request objects.

### Covered behavior

- JSON pretty-printing;
- unchanged plain text;
- body-only normal output;
- verbose request and response details;
- timing and size;
- POST body display;
- HEAD headers without a body;
- correct HEAD method in verbose output.

### Test count

8 tests.

### Why a fake response is used

Formatting does not need a real server. A fake object makes tests fast, deterministic, and focused only on formatting behavior.

---

## `tests/test_client.py`

### Purpose

Tests networking logic without making real network requests.

### Testing techniques

- `monkeypatch` replaces `requests.request` with a local fake function.
- captured keyword arguments show exactly what the client attempted to send.
- `SimpleNamespace` creates fake request and response objects.
- `Mock` checks whether uploaded files are closed.

### Covered behavior

- GET method and basic request settings;
- HEAD method override;
- default User-Agent;
- custom User-Agent;
- automatic form Content-Type;
- preservation of custom Content-Type;
- form data priority over raw body;
- forwarding timeout, TLS, redirects, auth, and cookies;
- storage of prepared request headers;
- timeout exception translation;
- connection exception translation;
- upload-file cleanup.

### Test count

12 tests.

### Why the network is mocked

Real endpoints can be slow, unavailable, rate-limited, or change behavior. Mocking makes the suite reliable and tests the client logic directly.

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
56 passed
85% total coverage
```

The lower total is mainly influenced by `main.py`, which is not currently tested as an end-to-end CLI entry point.

High coverage does not prove that no bugs exist. It means the tests executed a large percentage of measured statements. Test quality still depends on whether the assertions cover meaningful behavior.

---


# 11. File responsibility cheat sheet

| File | Main responsibility |
|---|---|
| `main.py` | Coordinates the complete application |
| `cli/parser.py` | Defines and parses CLI options |
| `cli/validator.py` | Validates user input |
| `core/methods.py` | Lists supported HTTP methods |
| `core/request.py` | Stores outgoing request settings |
| `core/client.py` | Sends requests and handles network errors |
| `core/response.py` | Wraps response data and calculations |
| `output/formatter.py` | Builds normal, verbose, and HEAD output |
| `output/printer.py` | Prints or saves formatted output |
| `utils/helpers.py` | Parses headers, auth, cookies, and forms |
| `utils/errors.py` | Defines custom application exceptions |
| `tests/test_validator.py` | Tests validation |
| `tests/test_helpers.py` | Tests helper parsing |
| `tests/test_parser.py` | Tests CLI parsing |
| `tests/test_formatter.py` | Tests output formatting |
| `tests/test_client.py` | Tests request-sending logic with mocks |
| `README.md` | Public installation and usage guide |
| `requirements.txt` | Records dependencies |
| `.gitignore` | Excludes generated and local files |

---

## Final mental model

The most important concept to remember is:

> `main.py` coordinates, the CLI layer understands the user, the utility layer converts values, the core layer performs HTTP work, the output layer presents the result, and the tests verify each responsibility independently.
