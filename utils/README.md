# `utils/` Directory Documentation

## Directory purpose

The `utils/` directory contains reusable conversion, file-handling, cleanup, and error-definition logic shared by the rest of MyCurl.

```text
utils/
├── errors.py
└── helpers.py
```

## Responsibility map

| File | Responsibility |
|---|---|
| `helpers.py` | Convert raw CLI strings and manage utility file operations |
| `errors.py` | Define typed application failures |

## Directory flow

```text
raw CLI strings
      |
      v
helper functions
      |
      v
structured values
      |
      v
Request / Client / main.py
```

---

# `helpers.py`

## Responsibility

Converts text from argparse into structured Python values and manages upload and cookie-file resources.

## Main functions

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

List of strings:

```python
[
    "Accept: application/json",
    "X-Test: value",
]
```

### Output

Dictionary:

```python
{
    "Accept": "application/json",
    "X-Test": "value",
}
```

### Splitting rule

Uses the first colon only:

```python
header.split(":", 1)
```

This preserves values containing colons.

Example:

```text
Authorization: Bearer abc:def
```

### Validation relationship

`cli.validator.validate_headers()` runs first, so helper parsing expects correctly structured header strings.

### Tests

- one header;
- multiple headers;
- colon inside value.

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

### Splitting rule

Uses the first colon only:

```python
auth.split(":", 1)
```

A password may contain additional colons.

### Empty input

Returns `None`.

### Validation relationship

`validate_auth()` checks the separator and non-empty username before parsing.

### Tests

- normal authentication;
- password containing colons;
- no authentication.

---

## `parse_cookies(cookie)`

### Input

Semicolon-separated cookie string:

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

Each pair:

- must contain `=`;
- must have a non-empty name.

Malformed input raises:

```python
InvalidCookieException
```

Examples:

```text
malformed_cookie
=abc123
```

### Why validation and parsing are combined

The string must be split into individual cookie pairs to validate each name/value entry, so one function performs both tasks.

### Empty input

Returns an empty dictionary.

### Tests

- one cookie;
- multiple cookies;
- no cookies;
- missing separator;
- empty name.

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

### Normal fields

Values not beginning with `@` enter the `data` dictionary.

### File fields

Values beginning with `@`:

1. remove the `@`;
2. open the path in `rb` mode;
3. store the file object in `files`.

### Missing or inaccessible files

Raises:

```python
FileUploadException
```

### Partial-failure cleanup

Example:

```text
first=@exists.txt
second=@missing.txt
```

If the first file opens and the second fails, the function closes every already opened file before re-raising the error.

This prevents file-handle leaks before control reaches `Client.send()`.

### Validation relationship

`validate_forms()` checks `=` and non-empty field names before parsing.

### Ownership lifecycle

```text
parse_forms opens file
       |
       +-- parsing failure -> parse_forms closes it
       |
       +-- parsing success -> Client.send owns it
                                  |
                                  +-- finally closes it
```

### Tests

- normal form data;
- cleanup when a later file fails.

---

## `save_cookies(cookies, filename)`

### Purpose

Writes response cookies using Netscape cookie-file format.

### File contents

Each row stores:

- domain;
- include-subdomains flag;
- path;
- secure flag;
- expiration;
- name;
- value.

### Header

```text
# Netscape HTTP Cookie File
```

### File-system errors

Any `OSError` becomes:

```python
FileWriteException
```

### Empty filename

Returns without writing.

### Tests

Invalid cookie-jar path is tested.

### Usage

Called from `main.py` after a successful response when `-c` is supplied.

---

# `errors.py`

## Responsibility

Defines custom exception types representing failures MyCurl understands.

## Why custom exceptions exist

They allow code to react to categories instead of parsing message strings.

Example:

```python
except TLSException as error:
    print(f"mycurl: {error}")
    sys.exit(1)
```

## Validation exceptions

| Exception | Meaning |
|---|---|
| `InvalidURLException` | URL is missing HTTP/HTTPS structure |
| `InvalidMethodException` | Method is unsupported |
| `InvalidHeaderException` | Header syntax is invalid |
| `InvalidTimeoutException` | Timeout is zero or negative |
| `InvalidAuthException` | Authentication syntax is invalid |
| `InvalidFormException` | Form syntax is invalid |
| `InvalidCookieException` | Cookie syntax is invalid |

## Networking exceptions

| Exception | Meaning |
|---|---|
| `RequestTimeoutException` | Request exceeded timeout |
| `TooManyRedirectsException` | Redirect limit exceeded |
| `TLSException` | Certificate verification failed |
| `ConnectionException` | Connection could not be established |
| `RequestFailedException` | Another Requests-level failure occurred |

## File exceptions

| Exception | Meaning |
|---|---|
| `FileUploadException` | Upload file could not be opened |
| `FileWriteException` | Output or cookie file could not be written |

## Exception translation layers

```text
arg or helper failure
      -> custom exception
      -> main.py
      -> readable CLI error
```

```text
Requests exception
      -> Client.send
      -> custom exception
      -> main.py
      -> readable CLI error
```

```text
OSError
      -> helper or printer
      -> FileWriteException / FileUploadException
      -> main.py
      -> readable CLI error
```

## Empty exception classes

The classes may contain only:

```python
pass
```

Their value comes from their distinct types.

## Tests

`utils/errors.py` reaches 100% measured coverage because all classes are imported and used across test modules.

---

## Utility directory design principles

### Conversion without orchestration

Helpers convert values but do not coordinate the application.

### Typed failures

Every meaningful failure category uses a distinct exception.

### Resource safety

Opened files are closed at the stage that owns them.

### Reusability

Functions are small and can be tested without networking.

## Directory maintenance checklist

- Split only once when values may contain separators.
- Validate names before storing dictionaries.
- Convert `OSError` to custom exceptions.
- Close partially opened resources.
- Add tests for malformed and empty values.
- Add new exceptions only for meaningful categories.
