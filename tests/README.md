# MyCurl Test Suite

This directory contains the complete automated test suite for MyCurl 2.1.

The suite combines unit tests, mocked networking tests, direct application-coordinator tests, and subprocess-level command-line tests.

## Current result

```text
109 tests passed
100% total coverage
0 missed statements
```

Run the full suite:

```powershell
python -m pytest -v
```

Run the coverage report:

```powershell
python -m pytest --cov=. --cov-report=term-missing
```

---

## Test directory structure

```text
tests/
├── README.md
├── test_cli.py
├── test_client.py
├── test_formatter.py
├── test_helpers.py
├── test_main.py
├── test_parser.py
├── test_printer.py
├── test_request.py
├── test_response.py
└── test_validator.py
```

---

## Testing strategy

The suite is organized into several layers.

```text
Unit tests
├── parser
├── validator
├── helpers
├── request model
├── response model
├── formatter
└── printer

Mocked integration tests
└── HTTP client

Direct coordinator tests
└── main()

End-to-end tests
└── CLI subprocess behavior
```

Each layer serves a different purpose:

| Layer | Purpose |
|---|---|
| Unit tests | Verify individual functions, classes, and branches |
| Mocked integration tests | Verify networking behavior without internet access |
| Direct coordinator tests | Verify `main()` orchestration and exception handling |
| End-to-end tests | Verify real CLI output and process exit codes |

---

# Test files

## `test_cli.py`

### Purpose

Tests the real command-line application by launching `main.py` in a subprocess.

### Covered behavior

- `--version`
- `--help`
- invalid URLs
- invalid headers
- malformed cookies
- invalid authentication
- invalid forms
- invalid timeout values
- nonexistent upload files
- non-zero error exit codes
- absence of raw Python tracebacks

### Why subprocess tests matter

These tests verify what a user actually experiences:

- command-line parsing;
- standard output;
- standard error;
- process exit status;
- executable entry-point behavior.

### Test count

```text
9 tests
```

---

## `test_client.py`

### Purpose

Tests the HTTP client without making real network requests.

### Testing tools

- `monkeypatch`
- fake request functions
- fake response objects
- `SimpleNamespace`
- `Mock`

### Covered behavior

- GET requests
- HEAD override
- default User-Agent
- custom User-Agent
- automatic Content-Type
- custom Content-Type preservation
- form-data priority over raw body
- timeout forwarding
- TLS verification forwarding
- redirect forwarding
- authentication forwarding
- cookie forwarding
- prepared request headers
- timeout exception translation
- excessive redirect translation
- TLS exception translation
- connection exception translation
- fallback Requests exception translation
- upload-file cleanup

### Why networking is mocked

Real endpoints can be unavailable, slow, rate-limited, or change their behavior. Mocking keeps the suite fast and deterministic.

### Test count

```text
15 tests
```

---

## `test_formatter.py`

### Purpose

Tests terminal-output formatting.

### Covered behavior

- JSON pretty-printing
- plain-text responses
- normal body output
- verbose request details
- verbose response details
- default prepared headers
- custom prepared headers
- request-body display
- elapsed-time display
- response-size display
- HEAD output without a body
- verbose HEAD method display

### Test count

```text
8 tests
```

---

## `test_helpers.py`

### Purpose

Tests parsing, cookie writing, upload handling, and cleanup helpers.

### Covered behavior

- single header parsing
- multiple header parsing
- colons inside header values
- authentication parsing
- colons inside passwords
- absent authentication
- single cookie parsing
- multiple cookie parsing
- absent cookies
- malformed cookies
- empty cookie names
- form-data parsing
- partial upload cleanup
- invalid cookie-jar paths
- successful cookie-jar writing
- no-op cookie saving without a filename

### Test count

```text
16 tests
```

---

## `test_main.py`

### Purpose

Tests the `main()` coordinator directly inside pytest.

### Covered behavior

- default GET selection
- automatic POST selection
- explicit method preservation
- validation invocation
- form parsing
- header parsing
- authentication parsing
- cookie parsing
- `Request` construction
- `Client.send()` invocation
- cookie saving
- response formatting
- terminal output
- binary-file output routing
- every handled custom exception
- error messages
- exit code `1`
- `if __name__ == "__main__"` execution
- version output

### Why this file is separate from `test_cli.py`

`test_main.py` measures and verifies internal orchestration directly.

`test_cli.py` verifies real command-line behavior from a user's perspective.

Both are useful and should remain.

### Test count

```text
18 tests after parameter expansion
```

---

## `test_parser.py`

### Purpose

Tests the `argparse` configuration directly.

### Technique

The tests replace `sys.argv` with `monkeypatch`, then call `parse_args()`.

### Covered behavior

- URL parsing
- default values
- decimal timeout values
- custom methods
- repeated headers
- request bodies
- verbose mode
- redirect following
- authentication
- cookies
- repeated forms
- HEAD mode
- output filenames

### Test count

```text
10 tests
```

---

## `test_printer.py`

### Purpose

Tests output destinations and file-writing behavior.

### Covered behavior

- terminal output
- exact binary-byte output
- invalid output paths
- `FileWriteException`

### Test count

```text
3 tests
```

---

## `test_request.py`

### Purpose

Tests the internal outgoing `Request` model.

### Covered behavior

- every constructor argument is stored correctly
- method
- URL
- headers
- body
- timeout
- verbose mode
- redirect behavior
- TLS behavior
- authentication
- User-Agent
- output filename
- HEAD mode
- cookies
- cookie jar
- form data
- upload files
- current optional-value behavior

### Test count

```text
2 tests
```

---

## `test_response.py`

### Purpose

Tests the internal incoming `Response` wrapper.

### Covered behavior

- status code
- reason
- response headers
- decoded body
- raw content bytes
- final URL
- elapsed time
- cookies
- redirect history
- prepared outgoing headers
- elapsed seconds
- response size in bytes

### Test count

```text
2 tests
```

---

## `test_validator.py`

### Purpose

Tests all validation functions and the top-level validation coordinator.

### Covered behavior

- valid HTTP and HTTPS URLs
- empty URLs
- missing URL schemes
- malformed URLs
- unsupported schemes
- valid methods
- lowercase methods
- absent custom methods
- unsupported methods
- valid headers
- repeated headers
- missing header separators
- empty header names
- valid integer timeouts
- valid decimal timeouts
- zero timeouts
- negative timeouts
- valid authentication
- absent authentication
- missing authentication separators
- empty usernames
- valid forms
- missing form separators
- empty form names
- complete `validate(args)` execution

### Testing tools

- `pytest.raises`
- `pytest.mark.parametrize`
- `SimpleNamespace`

### Test count

```text
26 tests after parameter expansion
```

---

# Test-count summary

| File | Tests |
|---|---:|
| `test_cli.py` | 9 |
| `test_client.py` | 15 |
| `test_formatter.py` | 8 |
| `test_helpers.py` | 16 |
| `test_main.py` | 18 |
| `test_parser.py` | 10 |
| `test_printer.py` | 3 |
| `test_request.py` | 2 |
| `test_response.py` | 2 |
| `test_validator.py` | 26 |
| **Total** | **109** |

---

# Coverage

Current measured coverage:

```text
Name                      Stmts   Miss  Cover
------------------------------------------------
cli/parser.py                25      0   100%
cli/validator.py             45      0   100%
core/client.py               29      0   100%
core/methods.py               1      0   100%
core/request.py              18      0   100%
core/response.py             37      0   100%
main.py                      69      0   100%
output/formatter.py          47      0   100%
output/printer.py            10      0   100%
tests/test_cli.py            51      0   100%
tests/test_client.py        134      0   100%
tests/test_formatter.py      68      0   100%
tests/test_helpers.py        70      0   100%
tests/test_main.py           99      0   100%
tests/test_parser.py         51      0   100%
tests/test_printer.py        15      0   100%
tests/test_request.py        26      0   100%
tests/test_response.py       23      0   100%
tests/test_validator.py      59      0   100%
utils/errors.py              28      0   100%
utils/helpers.py             61      0   100%
------------------------------------------------
TOTAL                       966      0   100%
```

## What 100% coverage means

Every measured statement was executed during the test run.

It does not prove that no bug can exist, but it confirms that every current statement is reached by at least one automated test.

The suite focuses on meaningful behavior in addition to line execution.

---

# Running tests

## Run everything

```powershell
python -m pytest -v
```

## Run coverage

```powershell
python -m pytest --cov=. --cov-report=term-missing
```

## Run one test file

```powershell
python -m pytest tests/test_client.py -v
```

## Run one specific test

```powershell
python -m pytest tests/test_cli.py::test_invalid_form_exits_with_error -v
```

## Stop after the first failure

```powershell
python -m pytest -x
```

## Show shorter output

```powershell
python -m pytest -q
```

## Re-run the last failed tests

```powershell
python -m pytest --lf
```

---

# Test design principles

## Avoid unnecessary internet access

Client tests mock Requests so they remain reliable.

## Test every bug fix

Each fixed issue should receive a regression test that fails before the fix and passes afterward.

## Test behavior, not implementation details

Tests should focus on externally meaningful results:

- returned values;
- forwarded arguments;
- output text;
- written bytes;
- exceptions;
- exit codes;
- resource cleanup.

## Keep tests isolated

A failure in one module should not depend on an unrelated public server or local machine state.

## Use temporary paths

File-writing tests should use pytest's `tmp_path` whenever possible.

## Verify cleanup

Tests involving opened files should assert that file handles are closed.

## Keep subprocess tests

Even though `main()` is tested directly, subprocess tests still verify the real CLI interface.

---

# Adding tests for a new feature

When adding a new CLI feature:

1. Add parser tests.
2. Add validation tests when rules are required.
3. Add helper tests when text conversion is required.
4. Add `Request` tests for new stored fields.
5. Add client tests for new Requests arguments.
6. Add formatter or printer tests for new output.
7. Add direct `main()` tests for orchestration.
8. Add subprocess tests for user-visible CLI behavior.
9. Run the full suite.
10. Update the test count and coverage documentation.

---

# Final verification

```powershell
python -m pytest
python -m pytest --cov=. --cov-report=term-missing
```

Expected:

```text
109 passed
100% total coverage
0 missed statements
```
