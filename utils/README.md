# MyCurl Utility Layer

This directory contains reusable conversion, file-handling, cleanup, and exception-definition logic for MyCurl 2.1.

```text
utils/
├── README.md
├── errors.py
└── helpers.py
```

## Current quality status

```text
utils/errors.py     100% coverage
utils/helpers.py    100% coverage
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
| `helpers.py` | Convert CLI strings and manage utility file operations |
| `errors.py` | Define typed MyCurl failures |

## Utility flow

```text
raw CLI strings
      |
      v
helper functions
      |
      v
structured Python values
      |
      v
Request / Client / main.py
```

---

# `helpers.py`

## Purpose

Converts raw argument strings into structured values and manages upload and cookie-file resources.

## Public functions

```python
parse_headers(headers)
parse_auth(auth)
parse_cookies(cookie)
parse_forms(forms)
save_cookies(cookies, filename)
```

---

## `parse_headers(headers)`

### Input

```python
[
    "Accept: application/json",
    "X-Test: hello",
]
```

### Output

```python
{
    "Accept": "application/json",
    "X-Test": "hello",
}
```

### Splitting behavior

Uses the first colon only:

```python
header.split(":", 1)
```

This preserves values containing additional colons.

Example:

```text
Authorization: Bearer abc:def
```

### Validation relationship

`cli.validator.validate_headers()` checks syntax first.

---

## `parse_auth(auth)`

### Input

```text
username:password
```

### Output

```python
("username", "password")
```

### Splitting behavior

Uses:

```python
auth.split(":", 1)
```

so passwords may contain additional colons.

### No authentication

Returns:

```python
None
```

### Validation relationship

`validate_auth()` checks:

- separator exists;
- username is not empty.

---

## `parse_cookies(cookie)`

### Input

```text
session=abc123; theme=dark
```

### Output

```python
{
    "session": "abc123",
    "theme": "dark",
}
```

### Validation performed here

Every cookie pair must:

- contain `=`;
- have a non-empty name.

Invalid input raises:

```python
InvalidCookieException
```

Rejected examples:

```text
malformed_cookie
=abc123
```

### No cookies

Returns an empty dictionary.

### Why validation happens here

The string must be split into individual cookie pairs before each name can be checked.

---

## `parse_forms(forms)`

### Purpose

Separates normal form fields from file uploads.

### Input examples

```text
name=Reo
role=developer
file=@example.txt
```

### Output

Tuple:

```python
(data, files)
```

Example:

```python
data = {
    "name": "Reo",
    "role": "developer",
}

files = {
    "file": <opened binary file>,
}
```

---

## Normal form fields

Values not beginning with `@` are stored in `data`.

## File fields

Values beginning with `@`:

1. remove `@`;
2. open the file in `rb` mode;
3. store the file object in `files`.

## Missing or inaccessible files

Raise:

```python
FileUploadException
```

---

## Partial-failure cleanup

Example:

```text
first=@exists.txt
second=@missing.txt
```

If the first file opens and the second fails, `parse_forms()` closes all already opened files before re-raising the error.

This prevents leaks before control reaches the client.

## Resource ownership

```text
parse_forms opens files
       |
       +-- parsing fails
       |      |
       |      v
       |  parse_forms closes files
       |
       +-- parsing succeeds
              |
              v
          Client.send owns files
              |
              v
          finally closes files
```

---

## `save_cookies(cookies, filename)`

### Purpose

Writes response cookies in Netscape cookie-file format.

### Stored fields

- domain;
- subdomain flag;
- path;
- secure flag;
- expiration;
- cookie name;
- cookie value.

### File header

```text
# Netscape HTTP Cookie File
```

### No filename

Returns without writing.

### File-system failure

Any `OSError` becomes:

```python
FileWriteException
```

### Used by

```text
main.py
```

after a successful response when `-c` is supplied.

---

## Helper tests

`tests/test_helpers.py` contains 16 tests.

Covered behavior:

- one header;
- multiple headers;
- colon inside a header value;
- authentication;
- colon inside a password;
- no authentication;
- one cookie;
- multiple cookies;
- no cookies;
- malformed cookie;
- empty cookie name;
- normal form data;
- partial upload cleanup;
- invalid cookie-jar path;
- successful cookie-file output;
- no-op cookie saving without a filename.

Measured coverage:

```text
utils/helpers.py    100%
```

---

# `errors.py`

## Purpose

Defines custom exception types for failures MyCurl understands.

## Why custom exceptions are useful

They allow code to react to error categories instead of parsing strings.

Example:

```python
except TLSException as error:
    print(f"mycurl: {error}")
    sys.exit(1)
```

---

## Validation exceptions

| Exception | Meaning |
|---|---|
| `InvalidURLException` | URL is invalid |
| `InvalidMethodException` | Method is unsupported |
| `InvalidHeaderException` | Header syntax is invalid |
| `InvalidTimeoutException` | Timeout is zero or negative |
| `InvalidAuthException` | Authentication syntax is invalid |
| `InvalidFormException` | Form syntax is invalid |
| `InvalidCookieException` | Cookie syntax is invalid |

---

## Networking exceptions

| Exception | Meaning |
|---|---|
| `RequestTimeoutException` | Request exceeded timeout |
| `TooManyRedirectsException` | Redirect limit was exceeded |
| `TLSException` | TLS certificate verification failed |
| `ConnectionException` | Connection could not be established |
| `RequestFailedException` | Another Requests failure occurred |

---

## File exceptions

| Exception | Meaning |
|---|---|
| `FileUploadException` | Upload file could not be opened |
| `FileWriteException` | Output or cookie file could not be written |

---

## Exception flow

### Validation or helper failure

```text
invalid value
   |
   v
custom exception
   |
   v
main.py
   |
   v
readable error + exit code 1
```

### Requests failure

```text
Requests exception
   |
   v
Client.send()
   |
   v
MyCurl exception
   |
   v
main.py
   |
   v
readable error + exit code 1
```

### File-system failure

```text
OSError
   |
   v
helper or printer
   |
   v
FileUploadException / FileWriteException
   |
   v
main.py
```

---

## Empty exception classes

The exception classes may contain only:

```python
pass
```

Their value comes from their distinct types.

---

## Error tests

The exception classes are exercised across:

- validator tests;
- helper tests;
- client tests;
- printer tests;
- main tests;
- CLI subprocess tests.

Measured coverage:

```text
utils/errors.py    100%
```

---

# Utility design principles

## Conversion without orchestration

Helpers convert values but do not coordinate the application.

## Typed failures

Every meaningful category has a dedicated exception.

## Resource safety

Files are closed by the stage that owns them.

## Small, testable functions

Helper functions remain independent of networking.

---

# Adding a utility feature

1. Add a focused helper function.
2. Decide whether validation belongs in `cli/validator.py` or the helper.
3. Add a dedicated exception when the category is meaningful.
4. Convert `OSError` where appropriate.
5. Clean up any opened resources.
6. Add unit tests.
7. Add direct-main tests if orchestration changes.
8. Update documentation.

---

# Maintenance checklist

- Split only once when values may contain separators.
- Reject empty names where required.
- Convert file errors into custom exceptions.
- Close partially opened resources.
- Test malformed, empty, and successful paths.
- Keep helpers independent of networking.
- Keep both utility modules at 100% coverage.
