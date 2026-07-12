# MyCurl Core Layer

This directory contains the HTTP domain layer for MyCurl 2.1.

It defines supported methods, stores outgoing request configuration, sends HTTP and HTTPS requests, translates network failures, and wraps incoming responses.

```text
core/
├── README.md
├── client.py
├── methods.py
├── request.py
└── response.py
```

## Current quality status

```text
core/client.py      100% coverage
core/methods.py     100% coverage
core/request.py     100% coverage
core/response.py    100% coverage
```

The complete project currently reports:

```text
109 tests passed
100% total coverage
0 missed statements
```

---

# Directory responsibilities

| File | Responsibility |
|---|---|
| `methods.py` | Supported HTTP methods |
| `request.py` | Outgoing request data model |
| `client.py` | HTTP networking and error translation |
| `response.py` | Incoming response data model |

## Core flow

```text
validated and parsed values
          |
          v
       Request
          |
          v
     Client.send()
          |
          v
 requests.request(...)
          |
          v
       Response
```

---

# `methods.py`

## Purpose

Defines the HTTP methods officially supported by MyCurl.

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

## Why this file exists

It provides one source of truth for method validation.

`cli/validator.py` imports this tuple instead of hardcoding its own method list.

## Responsibilities

- declare supported methods;
- keep method names uppercase;
- provide a reusable constant.

## What it does not do

- choose default methods;
- send requests;
- validate URLs;
- format output.

Default method selection happens in `main.py`.

## Tests

Covered through method-validation tests.

Measured coverage:

```text
core/methods.py    100%
```

---

# `request.py`

## Purpose

Defines the internal outgoing `Request` object.

## Main class

```python
Request
```

The class stores every setting needed by the client and formatter.

## Why a model object is used

Without `Request`, functions would need many separate arguments:

```text
method
url
headers
body
timeout
verbose
redirects
TLS behavior
authentication
User-Agent
output
HEAD mode
cookies
cookie jar
form data
upload files
```

A model object keeps the configuration together and makes interfaces easier to understand.

---

## Stored attributes

| Attribute | Meaning |
|---|---|
| `method` | Selected HTTP method |
| `url` | Target URL |
| `headers` | Parsed request headers |
| `body` | Raw `-d` body |
| `timeout` | Maximum request duration |
| `verbose` | Verbose-output flag |
| `follow_redirects` | Redirect behavior |
| `insecure` | Whether TLS verification is disabled |
| `auth` | Authentication tuple or `None` |
| `user_agent` | Custom User-Agent or `None` |
| `output` | Output filename or `None` |
| `head` | HEAD-mode flag |
| `cookies` | Parsed cookie mapping or current optional value |
| `cookie_jar` | Cookie output filename |
| `form_data` | Normal form fields |
| `form_files` | Open upload-file objects |

## Default behavior

The constructor preserves or normalizes optional collection values according to the current implementation.

For example, headers are normalized to an empty dictionary when absent, while some optional fields may remain `None`.

## Created by

```text
main.py
```

## Used by

```text
core/client.py
output/formatter.py
```

## No side effects

`Request` does not:

- validate;
- open files;
- send requests;
- format output;
- print output.

It stores state only.

---

## Request tests

`tests/test_request.py` contains 2 tests.

Covered behavior:

- every supplied constructor value is stored;
- method;
- URL;
- headers;
- body;
- timeout;
- verbose behavior;
- redirects;
- TLS behavior;
- authentication;
- User-Agent;
- output filename;
- HEAD mode;
- cookies;
- cookie jar;
- form data;
- upload files;
- current optional-value behavior.

Measured coverage:

```text
core/request.py    100%
```

---

# `client.py`

## Purpose

Converts an internal `Request` object into an actual HTTP or HTTPS request through the `requests` package.

## Main class

```python
Client
```

## Main method

```python
send(request)
```

---

## Request preparation

### Copy headers

```python
headers = request.headers.copy()
```

This prevents client defaults from modifying the original request dictionary.

### Select User-Agent

Priority:

1. custom `-A` value;
2. default `MyCurl/2.1`.

### Add default Content-Type

When:

- a raw body exists;
- form data is absent;
- upload files are absent;
- the user did not provide Content-Type;

the client adds:

```text
application/x-www-form-urlencoded
```

### Select actual method

Normally:

```python
method = request.method
```

When HEAD mode is enabled:

```python
method = "HEAD"
```

---

## Requests arguments

The client forwards:

| Requests argument | Source |
|---|---|
| `method` | selected method |
| `url` | `request.url` |
| `headers` | completed headers |
| `data` | form data or raw body |
| `files` | upload dictionary |
| `timeout` | request timeout |
| `verify` | opposite of `request.insecure` |
| `allow_redirects` | `request.follow_redirects` |
| `auth` | authentication tuple |
| `cookies` | request cookies |

## Body priority

```python
data = (
    request.form_data
    if request.form_data
    else request.body
)
```

Form data takes priority over a raw body.

Files are passed separately.

---

## Prepared outgoing headers

After Requests prepares the outgoing request, the client reads:

```python
response.request.headers
```

These may include generated values such as:

- `Content-Length`;
- multipart boundaries;
- encoding headers.

The prepared headers are stored in the custom response wrapper for verbose output.

---

## Response wrapping

The external Requests response becomes:

```python
core.response.Response
```

This keeps the rest of MyCurl dependent on its own stable interface.

---

## Error translation

Catch order is important.

### Timeout

```text
requests.exceptions.Timeout
→ RequestTimeoutException
```

### Excessive redirects

```text
requests.exceptions.TooManyRedirects
→ TooManyRedirectsException
```

### TLS certificate failure

```text
requests.exceptions.SSLError
→ TLSException
```

### Connection failure

```text
requests.exceptions.ConnectionError
→ ConnectionException
```

### Remaining Requests failure

```text
requests.exceptions.RequestException
→ RequestFailedException
```

Specific exceptions must be caught before broader parent exceptions.

---

## Upload cleanup

A `finally` block closes every upload file after:

- success;
- timeout;
- redirect failure;
- TLS failure;
- connection failure;
- unexpected Requests failure.

Earlier parsing failures are handled inside `utils.helpers.parse_forms()`.

---

## Client tests

`tests/test_client.py` contains 15 tests.

Covered behavior:

- GET;
- HEAD override;
- default and custom User-Agent;
- automatic Content-Type;
- custom Content-Type preservation;
- form-data priority;
- timeout forwarding;
- TLS verification;
- redirects;
- authentication;
- cookies;
- prepared headers;
- timeout translation;
- redirect translation;
- TLS translation;
- connection translation;
- fallback translation;
- file cleanup.

The HTTP call is mocked.

Measured coverage:

```text
core/client.py    100%
```

---

# `response.py`

## Purpose

Wraps a third-party Requests response in a MyCurl-specific object.

## Main class

```python
Response
```

## Stored data

| Attribute | Source |
|---|---|
| `status_code` | `response.status_code` |
| `reason` | `response.reason` |
| `headers` | `response.headers` |
| `body` | decoded `response.text` |
| `content` | raw `response.content` bytes |
| `url` | final response URL |
| `elapsed` | Requests elapsed time |
| `cookies` | response cookies |
| `history` | redirect history |
| `sent_headers` | prepared outgoing headers |

---

## Text and bytes

The wrapper stores both forms:

```python
body = response.text
content = response.content
```

| Representation | Purpose |
|---|---|
| text | terminal display and JSON formatting |
| bytes | binary output and byte-size calculation |

---

## Getter methods

```python
get_status_code()
get_headers()
get_body()
get_content()
get_reason()
get_url()
get_elapsed()
get_cookies()
get_history()
get_sent_headers()
```

## Calculated methods

### Elapsed seconds

```python
get_elapsed_seconds()
```

uses:

```python
self.elapsed.total_seconds()
```

### Response size

```python
get_size()
```

returns:

```python
len(self.content)
```

The value is measured in bytes.

---

## Response consumers

- `output/formatter.py`;
- `output/printer.py`;
- cookie-saving logic in `main.py`.

---

## Response tests

`tests/test_response.py` contains 2 tests.

Covered behavior:

- status code;
- reason;
- response headers;
- text body;
- raw bytes;
- final URL;
- elapsed time;
- cookies;
- redirect history;
- prepared headers;
- elapsed seconds;
- response size.

Measured coverage:

```text
core/response.py    100%
```

---

# Core design principles

## Separate outgoing and incoming models

```text
Request  = outgoing intent
Response = incoming result
```

## Isolate external networking

Only `client.py` performs Requests networking.

## Preserve resources safely

- `parse_forms()` owns files during parsing;
- `Client.send()` owns them during networking;
- both stages clean up their own failures.

## Translate external failures

Requests-specific exceptions are converted into MyCurl exceptions before reaching `main.py`.

---

# Adding a core feature

When adding a new request behavior:

1. Add a `Request` field if required.
2. Update `main.py` construction.
3. Update `Client.send()`.
4. Update response storage if needed.
5. Add request-model tests.
6. Add client tests.
7. Add response tests.
8. Add direct-main tests.
9. Update the README and technical documentation.

---

# Maintenance checklist

- Supported method list matches validation.
- Request fields match `main.py`.
- Client forwards all options.
- User headers remain preserved.
- Exception order remains specific-to-general.
- Upload files close on every path.
- Response stores both text and raw bytes.
- Every core module remains at 100% coverage.
