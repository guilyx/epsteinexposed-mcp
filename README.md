# epsteinexposed-mcp

> Credits: Erwin Lejeune — 2026-02-22

[![CI](https://github.com/guilyx/epsteinexposed-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/guilyx/epsteinexposed-mcp/actions/workflows/ci.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/guilyx/epsteinexposed-mcp)](https://app.codacy.com/gh/guilyx/epsteinexposed-mcp/dashboard)
[![codecov](https://codecov.io/gh/guilyx/epsteinexposed-mcp/graph/badge.svg)](https://codecov.io/gh/guilyx/epsteinexposed-mcp)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/protocol-MCP-purple)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Model Context Protocol server exposing the [Epstein Exposed](https://epsteinexposed.com) public API as AI-agent tool calls.**

Plug directly into any MCP-compatible client (Claude Desktop, Cursor, SmolAgents, etc.) to search persons, documents, flight logs, and emails from the Epstein case files.

> **Disclaimer:** Inclusion in the Epstein Exposed database does not imply guilt or wrongdoing. All data is derived from publicly released government records.

## Tools

| Tool | Description |
|---|---|
| `search_persons` | Search/filter persons of interest by name and category |
| `get_person` | Get full detail for a person by slug (bio, aliases, stats) |
| `search_documents` | FTS5 full-text search across case documents |
| `search_flights` | Search flight logs by passenger, year, origin, destination |
| `cross_search` | Search across documents and emails simultaneously |

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Run via stdio (for MCP clients)
python -m src.server

# Or via the MCP CLI
mcp run src/server.py
```

## MCP Client Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "epstein-files": {
      "command": "epsteinexposed-mcp",
      "args": []
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "epstein-files": {
      "command": "epsteinexposed-mcp",
      "args": []
    }
  }
}
```

## Architecture

```
MCP Client (Claude, Cursor, SmolAgents)
    │
    │  JSON-RPC 2.0 (stdio / SSE)
    ▼
epsteinexposed-mcp (FastMCP)
    │
    │  AsyncEpsteinExposed (curl_cffi)
    ▼
epsteinexposed.com/api/v1
```

Powered by the [`epsteinexposed`](https://github.com/guilyx/epsteinexposed) Python package.

## Development

```bash
git clone https://github.com/guilyx/epsteinexposed-mcp.git
cd epsteinexposed-mcp
pip install -e ".[dev]"
pytest -v
```

## Documentation

Full docs available at the [docs site](https://guilyx.github.io/epsteinexposed-mcp) (VitePress).

## License

MIT
