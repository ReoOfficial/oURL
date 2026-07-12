# MyCurl Output Layer

This directory controls how MyCurl presents responses and where response data is sent.

```text
output/
├── README.md
├── formatter.py
└── printer.py
```

## Current quality status

```text
output/formatter.py    100% coverage
output/printer.py      100% coverage
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
| `formatter.py` | Builds terminal-display text |
| `printer.py` | Prints text or writes raw bytes |

The distinction is important:

```text
formatter = what output looks like
printer   = where output goes
```

## Output flow

```text
Request + Response
        |
        v
format_response(...)
        |
        v
formatted text
        |
        v
print_response(..., raw content)
       / \
terminal  file
```

---

# `formatter.py`

## Purpose

Builds normal, verbose, and HEAD terminal output.

## Public functions

```python
format_body(body)
format_response(request, response)
```

---

## `format_body(body)`

### Purpose

Pretty-prints valid JSON and preserves ordinary text.

### Behavior

1. Attempts to parse the body with `json.loads`.
2. Valid JSON is returned with indentation.
3. Invalid JSON or plain text is returned unchanged.

Example input:

```json
{"message":"hello"}
```

Example output:

```json
{
    "message": "hello"
}
```

### Unicode

Uses:

```python
ensure_ascii=False
```

so Unicode characters remain readable.

### Handled errors

- `json.JSONDecodeError`;
- `TypeError`.

---

## `format_response(request, response)`

### Purpose

Creates the complete terminal-output string.

## URL processing

Uses `urlparse` to obtain:

- Host;
- path;
- query string.

Example URL:

```text
https://example.com/test?name=Reo
```

Displayed path:

```text
/test?name=Reo
```

---

## Normal mode

Conditions:

```text
verbose = False
head = False
```

Output:

```text
formatted response body only
```

---

## Verbose mode

Verbose output includes:

### Outgoing request

- method;
- path;
- Host;
- prepared request headers;
- request body when present.

Prefix:

```text
>
```

Example:

```text
> POST /post HTTP/1.1
> Host: example.com
> User-Agent: MyCurl/2.1
> Accept: */*
> X-Test: hello
> Content-Type: application/x-www-form-urlencoded
```

The formatter includes custom prepared headers in addition to standard ones.

### Incoming response

- status line;
- response headers.

Prefix:

```text
<
```

Example:

```text
< HTTP/1.1 200 OK
< Content-Type: application/json
```

### Response body

Displayed unless HEAD mode is active.

### Statistics

```text
Time: 0.125s
Size: 512 bytes
```

---

## HEAD mode

### `-I` without `-v`

Displays:

- status line;
- response headers;
- no response body.

### `-I` with `-v`

Displays the outgoing method as:

```text
HEAD
```

even when the original default method began as GET.

---

## Prepared headers

The formatter reads:

```python
response.get_sent_headers()
```

This displays what Requests actually prepared, including generated headers.

---

## Current protocol display

The formatter currently displays:

```text
HTTP/1.1
```

as a fixed string.

The actual transport protocol may differ.

---

## Formatter tests

`tests/test_formatter.py` contains 8 tests.

Covered behavior:

- JSON;
- plain text;
- normal body;
- verbose request details;
- verbose response details;
- custom prepared headers;
- request body;
- elapsed time;
- response size;
- HEAD without body;
- verbose HEAD method.

Measured coverage:

```text
output/formatter.py    100%
```

---

# `printer.py`

## Purpose

Routes output to the terminal or a destination file.

## Public function

```python
print_response(
    output,
    filename=None,
    content=None,
)
```

---

## Terminal path

When `filename` is absent:

```python
print(output)
```

The formatted string may contain:

- body;
- verbose request details;
- response headers;
- timing;
- size;
- HEAD response information.

---

## File path

When `filename` is supplied:

1. opens the destination in binary mode;
2. writes raw response bytes;
3. prints a confirmation message.

```python
with open(filename, "wb") as file:
    file.write(content)
```

---

## Why binary mode matters

Text mode can corrupt:

- PNG images;
- ZIP archives;
- PDFs;
- executables;
- compressed responses;
- arbitrary binary data.

Writing bytes preserves the response exactly.

---

## Error handling

Any `OSError` becomes:

```python
FileWriteException
```

Examples:

- missing parent directory;
- permission denied;
- invalid path;
- inaccessible device;
- file-system error.

---

## Inputs

| Parameter | Meaning |
|---|---|
| `output` | formatted terminal text |
| `filename` | optional output path |
| `content` | raw response bytes |

## Outputs

- terminal text;
- raw file;
- confirmation message;
- `FileWriteException`.

---

## Printer tests

`tests/test_printer.py` contains 3 tests.

Covered behavior:

- terminal output;
- exact binary output;
- invalid output paths;
- custom file-write exception.

Measured coverage:

```text
output/printer.py    100%
```

---

# Formatter and printer separation

The two representations must stay separate:

```text
formatted text -> terminal
raw bytes      -> file
```

This prevents verbose text, JSON formatting, or newline conversion from corrupting downloaded files.

---

# Current limitations

- Verbose information is not yet separated to stderr.
- HTTP protocol text is fixed as `HTTP/1.1`.
- Large responses are loaded into memory instead of streamed.
- Terminal output depends on decoded response text.

---

# Possible future improvements

- separate verbose information to stderr;
- stream large downloads;
- display the actual HTTP protocol version;
- add silent mode;
- add progress output;
- support explicit overwrite policies;
- support response-header-only file output.

---

# Adding a new output feature

1. Decide whether it changes formatting or destination behavior.
2. Update `formatter.py` for terminal appearance.
3. Update `printer.py` for terminal/file routing.
4. Preserve binary-safe output.
5. Add formatter tests.
6. Add printer tests.
7. Add direct-main tests if orchestration changes.
8. Add CLI tests if user-visible behavior changes.
9. Update documentation.

---

# Maintenance checklist

- Normal mode remains body-only.
- HEAD never displays a response body.
- Verbose mode shows prepared headers.
- Custom headers are included.
- File output always writes bytes.
- Invalid paths use `FileWriteException`.
- Formatter and printer tests stay separate.
- Both output modules remain at 100% coverage.
