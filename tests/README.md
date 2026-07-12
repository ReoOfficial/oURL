# `tests/` Directory Documentation

## Directory purpose

The `tests/` directory verifies MyCurl at multiple levels:

1. pure validation and conversion;
2. parser configuration;
3. formatter and printer behavior;
4. mocked networking;
5. complete CLI subprocess behavior.

```text
tests/
├── test_cli.py
├── test_client.py
├── test_formatter.py
├── test_helpers.py
├── test_parser.py
├── test_printer.py
└── test_validator.py
```

## Current result

```text
82 passed
87% total coverage
```

## Test-layer architecture

```text
Unit tests
├── validator
├── helpers
├── parser
├── formatter
└── printer

Mocked integration tests
└── client + response wrapper

End-to-end tests
└── main.py subprocess
```

## Why different layers are useful

| Layer | Benefit |
|---|---|
| Unit | Fast and precise failure location |
| Mocked client | Tests networking logic without internet |
| CLI subprocess | Tests real output and exit behavior |

---

# `test_cli.py`

## Purpose

Executes the actual `main.py` program in child processes.

## Helper design

A helper similar to:

```python
run_mycurl(*arguments)
```

uses:

```python
subprocess.run(
    [sys.executable, str(MAIN_FILE), *arguments],
    capture_output=True,
    text=True,
    check=False,
)
```

## Why `sys.executable` is used

It guarantees that the subprocess runs with the same Python interpreter as pytest.

## Captured values

Each test can inspect:

- `returncode`;
- `stdout`;
- `stderr`.

## Covered behavior

### Successful metadata commands

- `--version`;
- `--help`.

### Validation failures

- invalid URL;
- malformed header;
- malformed cookie;
- invalid authentication;
- invalid form;
- invalid timeout;
- nonexistent upload file.

### Reliability assertions

Tests verify:

```python
result.returncode != 0
```

and:

```python
"Traceback" not in result.stderr
```

This ensures the CLI reports failure correctly without exposing a raw Python traceback.

## Test count

9.

## Coverage caveat

Standard pytest-cov runs in the parent process. Because `main.py` runs in child processes, the report may show `main.py` at 0% even though these tests genuinely execute it.

## Maintenance guidance

Add a CLI test when behavior depends on:

- process exit status;
- stdout/stderr;
- argparse behavior;
- main-level exception handling.

---

# `test_client.py`

## Purpose

Tests `Client.send()` without real internet access.

## Main tools

- `monkeypatch`;
- `SimpleNamespace`;
- `Mock`;
- fake response objects;
- captured keyword arguments.

## Request factory

A helper creates a request-like object with defaults. Individual tests override only relevant fields.

## Fake response factory

Creates the attributes expected by `core.response.Response`, including:

- status;
- headers;
- text;
- bytes;
- URL;
- elapsed time;
- cookies;
- redirect history;
- prepared request headers.

## Mocking strategy

```python
monkeypatch.setattr(
    client_module.requests,
    "request",
    fake_request,
)
```

This replaces the real network operation.

## Covered behavior

### Method and URL

- GET forwarding;
- HEAD override;
- target URL.

### Headers

- default User-Agent;
- custom User-Agent;
- generated form Content-Type;
- preserved custom Content-Type;
- prepared sent headers.

### Body and forms

- raw body;
- form-data priority.

### Options

- timeout;
- TLS verification;
- redirects;
- authentication;
- cookies.

### Exceptions

- timeout;
- excessive redirects;
- TLS;
- connection;
- generic Requests failure.

### Cleanup

- upload file `.close()` is called.

## Test count

15.

## Why real endpoints are avoided

External services may be:

- unavailable;
- slow;
- rate-limited;
- changed;
- geographically blocked.

Mocking makes tests deterministic and focused on MyCurl logic.

## Maintenance guidance

Any new argument passed to `requests.request()` should receive a captured-argument test.

---

# `test_formatter.py`

## Purpose

Tests text formatting in isolation.

## Test doubles

### `FakeResponse`

Returns controlled values for:

- status;
- headers;
- body;
- sent headers;
- elapsed time;
- size.

### Request factory

Uses `SimpleNamespace` with fields expected by the formatter.

## Covered behavior

- JSON becomes indented;
- plain text stays unchanged;
- normal mode displays body only;
- verbose mode displays request details;
- verbose mode displays response details;
- time and size are displayed;
- POST body is displayed;
- HEAD has no response body;
- verbose HEAD displays `HEAD`.

## Test count

8.

## Why no network is needed

The formatter depends only on interfaces, not on a live response.

## Maintenance guidance

Every change to output syntax should update or extend these assertions.

---

# `test_helpers.py`

## Purpose

Tests reusable parsing, validation, cookie writing, and cleanup behavior.

## Covered header behavior

- single header;
- repeated headers;
- colon inside value.

## Covered authentication behavior

- normal auth;
- password containing colons;
- absent auth.

## Covered cookie behavior

- one cookie;
- multiple cookies;
- absent cookies;
- malformed cookie;
- empty cookie name.

## Covered forms behavior

- normal fields;
- cleanup after partial file-open failure.

## Covered file behavior

- invalid cookie-jar destination raises `FileWriteException`.

## Mocking file opens

A fake `open()` can:

- return a mock file for one path;
- raise `FileNotFoundError` for another.

The test then verifies that the first handle was closed.

## Test count

14.

## Maintenance guidance

Add tests for any new parsing syntax or resource-cleanup branch.

---

# `test_parser.py`

## Purpose

Tests `argparse` configuration directly.

## Technique

`monkeypatch` replaces `sys.argv`.

Example:

```python
monkeypatch.setattr(
    sys,
    "argv",
    ["mycurl", "-v", "https://example.com"],
)
```

Then:

```python
args = parse_args()
```

## Covered behavior

- positional URL;
- defaults;
- decimal timeout;
- explicit method;
- repeated headers;
- request body;
- verbose and redirects;
- authentication and cookies;
- repeated forms;
- HEAD and output.

## Test count

10.

## Why not use subprocesses here?

Direct parser tests are faster and make parser-specific failures easier to diagnose.

## Maintenance guidance

Every new parser argument needs:

- default test;
- enabled-value test;
- repeated-value test when applicable;
- invalid-type CLI test when applicable.

---

# `test_printer.py`

## Purpose

Tests binary file output and file-system error conversion.

## Binary output test

1. Creates a temporary path using pytest's `tmp_path`.
2. Supplies known bytes.
3. Calls `print_response`.
4. Reads bytes back.
5. Asserts exact equality.

This proves no text decoding or newline conversion occurred.

## Invalid path test

Calls the printer with a missing parent directory and expects:

```python
FileWriteException
```

## Test count

2.

## Maintenance guidance

Future silent mode, overwrite policy, or streaming logic should be tested here.

---

# `test_validator.py`

## Purpose

Tests every semantic input validator.

## URL coverage

- valid HTTPS;
- empty value;
- missing scheme;
- malformed value;
- unsupported FTP scheme.

## Method coverage

- uppercase;
- lowercase;
- `None`;
- unsupported value.

## Header coverage

- valid one;
- valid repeated;
- missing colon;
- empty name.

## Timeout coverage

- valid integer;
- valid decimal;
- zero;
- negative values.

## Authentication coverage

- valid value;
- missing colon;
- empty username.

## Form coverage

- valid field;
- missing `=`;
- empty name.

## Techniques

### `pytest.raises`

```python
with pytest.raises(InvalidURLException):
    validate_url("example.com")
```

### `pytest.mark.parametrize`

Runs the same logic against multiple values.

## Test count

24 after parameter expansion.

## Maintenance guidance

Validators should always have:

- at least one valid test;
- each meaningful invalid branch;
- boundary values;
- error-type assertion.

---

## Coverage report interpretation

Latest measured module coverage:

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

`main.py` is exercised in subprocess tests but not automatically measured by the parent coverage process.

## Running tests

All tests:

```powershell
python -m pytest -v
```

Coverage:

```powershell
python -m pytest --cov=. --cov-report=term-missing
```

One file:

```powershell
python -m pytest tests/test_client.py -v
```

One test:

```powershell
python -m pytest tests/test_cli.py::test_invalid_form_exits_with_error -v
```

## Test directory maintenance checklist

- Tests do not depend unnecessarily on internet access.
- Every bug fix includes a regression test.
- Exit-code behavior is tested in subprocesses.
- File operations use temporary paths or mocks.
- New features update test counts in documentation.
- Coverage numbers are refreshed before release.
