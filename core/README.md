# `core/` Directory Documentation

## Directory purpose

The `core/` directory represents the HTTP domain of MyCurl. It defines supported methods, stores outgoing request configuration, sends requests through Requests, and wraps incoming responses.

```text
core/
├── client.py
├── methods.py
├── request.py
└── response.py
```

## Responsibility map

| File | Responsibility |
|---|---|
| `methods.py` | Supported HTTP methods |
| `request.py` | Outgoing request data model |
| `client.py` | Networking and transport error translation |
| `response.py` | Incoming response data model |

## Directory flow

```text
validated and parsed values
          |
          v
     Request object
          |
          v
      Client.send
          |
          v
  requests.request(...)
          |
          v
     Response object
```

---

# `methods.py`

## Responsibility

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

## Why it exists

This tuple acts as a single source of truth. `validator.py` imports it instead of maintaining its own copy.

## Runtime role

`methods.py` does not send requests or select defaults. It only defines which explicit methods validation accepts.

## Adding a method

To support another method:

1. add its uppercase name to `SUPPORTED_METHODS`;
2. verify Requests supports sending it;
3. add validation tests;
4. add client or end-to-end tests;
5. update documentation.

## Tests

Covered indirectly by method validation tests.

---

# `request.py`

## Responsibility

Defines the internal `Request` object containing all data needed by the networking and formatting layers.

## Main class

```python
Request
```

## Why a model object is used

Without `Request`, functions would need many separate parameters:

```text
method
url
headers
body
timeout
verbose
redirects
TLS option
auth
output
HEAD
cookies
cookie jar
form data
form files
```

A model object keeps related configuration together and makes interfaces easier to understand.

## Stored fields

| Attribute | Meaning |
|---|---|
| `method` | Selected HTTP method |
| `url` | Target URL |
| `headers` | Parsed request-header dictionary |
| `body` | Raw `-d` body |
| `timeout` | Maximum request duration |
| `verbose` | Verbose-output flag |
| `follow_redirects` | Redirect behavior |
| `insecure` | Whether TLS verification is disabled |
| `auth` | `(username, password)` tuple or `None` |
| `user_agent` | Custom User-Agent or `None` |
| `output` | Output filename or `None` |
| `head` | HEAD-mode flag |
| `cookies` | Cookie dictionary |
| `cookie_jar` | Cookie output filename |
| `form_data` | Normal multipart/form fields |
| `form_files` | Open binary upload-file objects |

## Mutable defaults

The class protects collection fields with patterns such as:

```python
self.headers = headers or {}
self.cookies = cookies or {}
self.form_data = form_data or {}
self.form_files = form_files or {}
```

This avoids shared mutable default arguments.

## Created by

`main.py`

## Consumed by

- `core.client.Client.send()`;
- `output.formatter.format_response()`.

## No networking responsibility

The class stores data only. It does not validate, parse, send, format, print, or save anything.

## Tests

The object is exercised indirectly through client and formatter tests using request-like objects. A future improvement could add direct constructor tests.

## Maintenance guidance

When adding a runtime feature:

- add a field only if it logically belongs to an outgoing request;
- update construction in `main.py`;
- update every consumer;
- add tests for defaults and propagation.

---

# `client.py`

## Responsibility

Converts the internal `Request` model into an actual HTTP/HTTPS operation through the `requests` package.

## Main class

```python
Client
```

## Main method

```python
send(request)
```

## Request preparation sequence

### 1. Copy headers

```python
headers = request.headers.copy()
```

This allows the client to add defaults without modifying the original request dictionary.

### 2. Select User-Agent

Priority:

1. custom `-A` value;
2. default `MyCurl/2.1`.

### 3. Add default Content-Type

When:

- a raw body exists;
- form data is absent;
- files are absent;
- the user did not supply Content-Type;

the client adds:

```text
application/x-www-form-urlencoded
```

### 4. Select actual method

Normally:

```python
method = request.method
```

For `-I`:

```python
method = "HEAD"
```

### 5. Call Requests

The client forwards:

| Requests argument | Source |
|---|---|
| `method` | selected method |
| `url` | `request.url` |
| `headers` | copied and completed headers |
| `data` | form data or raw body |
| `files` | upload dictionary |
| `timeout` | decimal or integer timeout |
| `verify` | opposite of `request.insecure` |
| `allow_redirects` | `request.follow_redirects` |
| `auth` | authentication tuple |
| `cookies` | cookie dictionary |

## Data priority

```python
data=request.form_data if request.form_data else request.body
```

Normal form fields take priority over a raw body. Files are sent through the separate `files` argument.

## Prepared outgoing headers

After Requests sends or prepares the request, the client reads:

```python
response.request.headers
```

These headers include automatically generated values such as:

- Content-Length;
- multipart Content-Type boundary;
- connection and encoding headers.

The wrapper stores them so verbose output shows what was actually prepared.

## Response wrapping

The external Requests response is converted into:

```python
core.response.Response
```

This prevents the rest of MyCurl from depending directly on every Requests implementation detail.

## Error translation

Catch order is important because some Requests exceptions inherit from broader ones.

### Timeout

```text
requests.exceptions.Timeout
    -> RequestTimeoutException
```

### Excessive redirects

```text
requests.exceptions.TooManyRedirects
    -> TooManyRedirectsException
```

### TLS verification

```text
requests.exceptions.SSLError
    -> TLSException
```

This must appear before the general connection handler.

### Connection failure

```text
requests.exceptions.ConnectionError
    -> ConnectionException
```

### Remaining Requests failure

```text
requests.exceptions.RequestException
    -> RequestFailedException
```

## File cleanup

A `finally` block closes all upload file objects after:

- success;
- timeout;
- redirect error;
- TLS error;
- connection error;
- unexpected Requests error.

Earlier parsing failures are handled separately inside `parse_forms()`.

## Inputs

One `Request` object.

## Output

One custom `Response` object.

## Tests

`tests/test_client.py` contains 15 tests covering:

- GET;
- HEAD override;
- default and custom User-Agent;
- generated Content-Type;
- preserved custom Content-Type;
- form-data priority;
- forwarded options;
- prepared headers;
- timeout translation;
- redirect translation;
- TLS translation;
- connection translation;
- fallback translation;
- upload cleanup.

The HTTP call is mocked so these tests do not depend on internet access.

## Maintenance guidance

- Catch specific exceptions before parent exceptions.
- Never leave upload files open.
- Preserve user headers unless a documented default is needed.
- Add tests for every new Requests option.
- Keep formatting out of this file.

---

# `response.py`

## Responsibility

Wraps the third-party Requests response and exposes a stable MyCurl-specific interface.

## Main class

```python
Response
```

## Constructor inputs

- external Requests response;
- optional prepared sent-header mapping.

## Stored fields

| Attribute | Source |
|---|---|
| `status_code` | `response.status_code` |
| `reason` | `response.reason` |
| `headers` | `response.headers` |
| `body` | `response.text` |
| `content` | `response.content` |
| `url` | `response.url` |
| `elapsed` | `response.elapsed` |
| `cookies` | `response.cookies` |
| `history` | `response.history` |
| `sent_headers` | prepared outgoing headers |

## Text and bytes

The wrapper stores both:

```python
body = response.text
content = response.content
```

They serve different purposes:

| Value | Used for |
|---|---|
| decoded text | terminal display and JSON formatting |
| raw bytes | response size and binary-safe `-o` output |

## Getter interface

Common getters include:

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

## Calculated values

### Elapsed seconds

```python
self.elapsed.total_seconds()
```

Returned by:

```python
get_elapsed_seconds()
```

### Response size

```python
len(self.content)
```

Returned by:

```python
get_size()
```

The size is measured in received bytes, not decoded characters.

## Consumers

- `output.formatter`;
- `output.printer`;
- cookie-saving logic in `main.py`.

## Maintenance note

Legacy getters referencing nonexistent response attributes should be removed or implemented before use.

## Tests

Response behavior is exercised by formatter, client, and printer tests. Additional direct tests could increase the file's measured coverage.

---

## Core directory design principles

### Model separation

`Request` represents outgoing intent.  
`Response` represents incoming result.

### External dependency isolation

Only `client.py` directly performs Requests networking.

### Stable interfaces

Other directories consume MyCurl objects and methods rather than relying on raw third-party objects.

### Resource ownership

- `parse_forms()` owns files during parsing;
- `Client.send()` owns them during networking;
- cleanup occurs in both failure stages.

## Directory maintenance checklist

- Supported method list and validation agree.
- Request fields match `main.py`.
- Client forwards all required options.
- Exception catch order remains specific-to-general.
- Response stores raw bytes.
- Upload files close on every path.
