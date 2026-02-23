# Getting Started

## Prerequisites

- **Python 3.12+**
- **pip** (or [uv](https://docs.astral.sh/uv/) for faster installs)

## Installation

```bash
# Clone the repository
git clone https://github.com/guilyx/epsteinexposed-mcp.git
cd epsteinexposed-mcp

# Install with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

### Run via stdio (default)

```bash
python -m src.server
```

The server starts in **stdio transport mode** — it reads JSON-RPC messages from stdin and writes responses to stdout. This is the standard way MCP clients (Claude Desktop, Cursor, etc.) communicate with tool servers.

### Run via the MCP CLI

```bash
mcp run src/server.py
```

### Use as a library

```python
from src.epstein_client import EpsteinClient

async with EpsteinClient() as client:
    persons = await client.search_persons("Doe")
    print(persons)
```

## Running Tests

```bash
pytest -v
```

## Linting

```bash
ruff check .
ruff format --check .
```

## What's Next?

- **[Architecture](/guide/architecture)** — understand how the pieces fit together
- **[Configuration](/guide/configuration)** — environment variables and tuning
- **[Tools API](/api/tools)** — reference for all MCP tools exposed
