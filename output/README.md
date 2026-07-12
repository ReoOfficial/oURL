# `output/` Directory Documentation

## Directory purpose

The `output/` directory controls presentation and destination. It converts response data into readable terminal text and writes raw response bytes to files.

```text
output/
├── formatter.py
└── printer.py
```

## Responsibility boundary

| File | Responsibility |
|---|---|
| `formatter.py` | What terminal output looks like |
| `printer.py` | Where output goes |

This separation allows formatting to be tested without writing files and file output to be tested without formatting HTTP data.

## Directory flow

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

## Responsibility

Builds terminal-friendly output for normal, verbose, and HEAD modes.

## Public functions

```python
format_body(body)
format_response(request, response)
```

---

## `format_body(body)`

### Purpose

Pretty-prints JSON while preserving ordinary text.

### Behavior

1. Attempts `json.loads(body)`.
2. If successful, returns indented JSON.
3. If parsing fails, returns the original body.

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

### Unicode behavior

`ensure_ascii=False` keeps readable Unicode characters instead of escaping them unnecessarily.

### Expected inputs

- decoded text;
- possibly empty text;
- non-JSON text;
- valid JSON.

### Errors handled

- `json.JSONDecodeError`;
- `TypeError`.

---

## `format_response(request, response)`

### Purpose

Creates the complete terminal display string according to request flags.

## URL processing

Uses `urlparse(request.url)` to obtain:

- network location for Host;
- path;
- query string.

Example:

```text
https://example.com/test?name=Reo
```

Verbose path:

```text
/test?name=Reo
```

## Normal mode

Conditions:

```text
verbose = False
head = False
```

Output:

- formatted response body only.

## Verbose mode

Conditions:

```text
verbose = True
```

Output contains:

### Outgoing request information

- method and path;
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
> Host: postman-echo.com
> User-Agent: MyCurl/2.1
> Content-Type: application/x-www-form-urlencoded
> Content-Length: 8
```

### Incoming response information

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

Printed unless HEAD mode is enabled.

### Statistics

```text
Time: 0.125s
Size: 19 bytes
```

## HEAD mode

### `-I` without `-v`

Output:

- status line;
- response headers;
- no body.

### `-I` with `-v`

Outgoing method is displayed as:

```text
HEAD
```

rather than the original default method.

## Prepared header use

The formatter uses:

```python
response.get_sent_headers()
```

This displays actual prepared headers rather than only user-provided headers.

## Protocol display

The status and request lines currently display `HTTP/1.1` as a fixed string. The actual transport may differ.

## Inputs

- internal `Request`;
- internal `Response`.

## Output

One formatted string.

## Tests

`tests/test_formatter.py` contains 8 tests for:

- JSON;
- plain text;
- normal body;
- verbose request and response;
- statistics;
- POST body;
- HEAD without body;
- verbose HEAD method.

## Maintenance guidance

- Keep file writing out of the formatter.
- Keep transport logic out of the formatter.
- Add tests for every new output mode.
- Avoid ANSI formatting unless file output and terminal detection are handled carefully.
- Future cURL parity should separate verbose output to stderr.

---

# `printer.py`

## Responsibility

Routes data to the terminal or a file and converts file-system failures into project-specific errors.

## Public function

```python
print_response(output, filename=None, content=None)
```

## Terminal path

When `filename` is absent:

```python
print(output)
```

The formatted string may include:

- body;
- verbose headers;
- timing;
- size;
- HEAD response headers.

## File path

When `filename` exists:

1. opens destination in `wb` mode;
2. writes raw response bytes;
3. prints a success confirmation.

```python
with open(filename, "wb") as file:
    file.write(content)
```

## Why binary mode matters

Text mode can corrupt:

- PNG images;
- ZIP archives;
- PDFs;
- executables;
- compressed data;
- arbitrary binary responses.

Raw bytes preserve the server response exactly.

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
- file-system failure.

## Inputs

| Parameter | Meaning |
|---|---|
| `output` | formatted terminal text |
| `filename` | optional destination |
| `content` | raw response bytes |

## Output

- terminal text;
- raw output file;
- success message;
- `FileWriteException`.

## Tests

`tests/test_printer.py` contains:

1. invalid path test;
2. exact binary-byte output test.

## Interaction with formatter

The two representations must not be confused:

```text
formatted output -> terminal
raw content      -> file
```

## Maintenance guidance

When adding progress bars, silent mode, or stderr behavior, preserve binary output and keep terminal-only decorations out of saved files.

---

## Output directory known limitations

- Verbose data is not yet separated to stderr.
- HTTP protocol text is fixed as HTTP/1.1.
- Very large downloads are held in memory instead of streamed.
- Terminal body output assumes decoded text.

## Directory maintenance checklist

- Normal output remains body-only.
- HEAD never prints a body.
- Verbose mode shows prepared headers.
- File output writes bytes.
- Invalid paths use `FileWriteException`.
- Printer and formatter tests remain separate.
