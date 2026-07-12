# MyCurl CLI Layer

This directory contains the command-line interface layer for MyCurl 2.1.

It defines how command-line arguments are parsed and how user input is validated before any network request or file operation begins.

```text
cli/
├── README.md
├── parser.py
└── validator.py
```

## Current quality status

```text
cli/parser.py       100% coverage
cli/validator.py    100% coverage
```

The complete project currently reports:

```text
109 tests passed
100% total coverage
0 missed statements
```

---

# Directory responsibilities

The CLI layer answers two separate questions:

| File | Responsibility |
|---|---|
| `parser.py` | What did the user type? |
| `validator.py` | Is the parsed value valid for MyCurl? |

Parsing and validation are intentionally separate.

```text
sys.argv
   |
   v
parse_args()
   |
   v
argparse.Namespace
   |
   v
validate(args)
   |
   v
validated Namespace
```

---

# `parser.py`

## Purpose

Defines the complete command-line interface with Python's `argparse` module.

## Public function

```python
parse_args()
```

The function returns an `argparse.Namespace` containing all parsed options.

## Parsed fields

Typical namespace fields include:

```text
url
method
header
data
form
head
user
cookie
cookie_jar
max_time
location
insecure
verbose
user_agent
output
```

---

## Supported arguments

### Target

#### `URL`

Required positional target URL.

```powershell
python main.py https://example.com
```

---

## Request options

### `-X`, `--request METHOD`

Sets an explicit HTTP method.

```powershell
python main.py -X DELETE https://example.com/resource
```

The parser stores the value. `validator.py` decides whether the method is supported.

### `-H`, `--header HEADER`

Adds a request header and may be repeated.

```powershell
python main.py `
  -H "Accept: application/json" `
  -H "X-Test: hello" `
  https://example.com
```

Because the option uses `action="append"`, the parser returns a list.

### `-d`, `--data DATA`

Stores a raw request body.

```powershell
python main.py -d "name=Reo" https://example.com
```

When no explicit method is supplied, `main.py` selects `POST`.

### `-F`, `--form FORM`

Adds normal form data or a file upload and may be repeated.

```powershell
-F "name=Reo"
-F "file=@example.txt"
```

### `-I`, `--head`

Enables HEAD behavior.

```powershell
python main.py -I https://example.com
```

---

## Authentication and cookies

### `-u`, `--user USER:PASS`

Stores basic-authentication text.

```powershell
python main.py -u "user:password" https://example.com
```

### `-b`, `--cookie COOKIE`

Stores a semicolon-separated cookie string.

```powershell
python main.py -b "session=abc123; theme=dark" https://example.com
```

### `-c`, `--cookie-jar FILE`

Stores the output filename for received cookies.

```powershell
python main.py -c cookies.txt https://example.com
```

---

## Connection options

### `--max-time SECONDS`

Uses `type=float`, so integer and decimal values are accepted.

```powershell
python main.py --max-time 5 https://example.com
python main.py --max-time 5.5 https://example.com
```

The default is:

```text
15.0 seconds
```

Argparse rejects non-numeric values. `validator.py` rejects zero and negative values.

### `-L`, `--location`

Enables redirect following.

### `-k`, `--insecure`

Disables TLS certificate verification.

---

## Output options

### `-v`, `--verbose`

Displays request and response details.

### `-A`, `--user-agent VALUE`

Overrides the default User-Agent.

### `-o`, `--output FILE`

Stores raw response bytes in a file.

---

## Metadata

### `--version`

Prints:

```text
MyCurl 2.1
```

### `--help`

Generated automatically by argparse.

---

## Argparse concepts used

| Feature | Usage |
|---|---|
| positional argument | Required URL |
| `action="append"` | Repeated headers and forms |
| `action="store_true"` | Boolean options |
| `type=float` | Decimal timeouts |
| `metavar` | Cleaner help output |
| argument groups | Organized help |
| `RawTextHelpFormatter` | Preserved examples |
| `action="version"` | Version output |

---

## Parser tests

`tests/test_parser.py` contains 10 tests covering:

- URL parsing;
- default values;
- decimal timeouts;
- custom methods;
- repeated headers;
- request data;
- verbose mode;
- redirects;
- authentication;
- cookies;
- repeated forms;
- HEAD mode;
- output filenames.

Measured coverage:

```text
cli/parser.py    100%
```

---

# `validator.py`

## Purpose

Checks whether parsed values are valid for MyCurl.

## Public coordinator

```python
validate(args)
```

This function calls every individual validator and returns the same namespace when all checks pass.

---

## `validate_url(url)`

Uses `urllib.parse.urlparse`.

Requirements:

- scheme must be `http` or `https`;
- network location must be present.

Accepted:

```text
https://example.com
http://localhost:8000
```

Rejected:

```text
example.com
ftp://example.com
file:///example.txt
not-a-url
```

Raises:

```python
InvalidURLException
```

---

## `validate_method(method)`

Behavior:

- accepts `None`;
- compares methods in uppercase;
- checks `core.methods.SUPPORTED_METHODS`.

Raises:

```python
InvalidMethodException
```

---

## `validate_headers(headers)`

Each header must:

- contain `:`;
- have a non-empty name.

Accepted:

```text
Accept: application/json
Authorization: Bearer abc:def
```

Rejected:

```text
WrongHeader
: value
```

Raises:

```python
InvalidHeaderException
```

---

## `validate_timeout(timeout)`

Requires:

```text
timeout > 0
```

Accepted:

```text
15
5.5
0.1
```

Rejected:

```text
0
-1
-100
```

Raises:

```python
InvalidTimeoutException
```

---

## `validate_auth(auth)`

When supplied:

- must contain `:`;
- username must not be empty.

Accepted:

```text
user:password
user:password:with:colons
```

Rejected:

```text
missing-password
:password
```

Raises:

```python
InvalidAuthException
```

`None` is accepted when authentication is not used.

---

## `validate_forms(forms)`

Every form entry must:

- contain `=`;
- have a non-empty field name.

Accepted:

```text
name=Reo
file=@example.txt
```

Rejected:

```text
missing-equals
=value
```

Raises:

```python
InvalidFormException
```

---

## Validator dependencies

| Dependency | Purpose |
|---|---|
| `urllib.parse.urlparse` | URL structure |
| `core.methods.SUPPORTED_METHODS` | Supported-method source of truth |
| `utils.errors` | Typed validation failures |

---

## Validator tests

`tests/test_validator.py` contains 26 tests after parameter expansion.

Covered behavior includes:

- valid and invalid URLs;
- uppercase, lowercase, absent, and unsupported methods;
- valid and malformed headers;
- integer and decimal timeouts;
- zero and negative timeouts;
- valid, absent, and malformed authentication;
- valid and malformed forms;
- the complete `validate(args)` coordinator.

Measured coverage:

```text
cli/validator.py    100%
```

---

# Error flow

```text
invalid parsed value
       |
       v
validator function
       |
       v
custom exception
       |
       v
main.py handler
       |
       v
mycurl error message
       |
       v
exit code 1
```

---

# Adding a new CLI option

When adding a new flag:

1. Define it in `parser.py`.
2. Choose an appropriate destination name.
3. Add validation if the value has rules.
4. Add a `Request` field if runtime code needs it.
5. Add parser tests.
6. Add validator tests.
7. Add direct `main()` tests.
8. Add subprocess tests when output or exit behavior changes.
9. Update the root README and technical documentation.

---

# Maintenance checklist

- Parser defaults match runtime assumptions.
- Repeatable options use `action="append"`.
- Boolean flags use `action="store_true"`.
- Timeout remains `float`.
- Validation errors use dedicated exception types.
- New flags appear in help output.
- Parser and validator tests remain at 100% coverage.
