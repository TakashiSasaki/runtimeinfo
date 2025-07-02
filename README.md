# RuntimeInfo

Utilities for capturing runtime host information.

This package exposes a small CLI that prints system details such as hostname,
IP address and the current path.

```bash
runtimeinfo [PATH] [--json]
```

When `--json` is given, the output is canonical JSON; otherwise it is formatted
for readability.

## Running Tests

Install dependencies and run pytest within this directory:

```bash
pip install -e .
pytest -q
```

