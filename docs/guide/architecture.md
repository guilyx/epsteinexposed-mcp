# Architecture

## Overview

```
┌─────────────────┐     stdio / SSE      ┌─────────────────┐
│   MCP Client    │ ◀──────────────────▶  │  epstein-files  │
│  (AI Agent /    │    JSON-RPC 2.0       │    -mcp         │
│   Claude, etc.) │                       │                 │
└─────────────────┘                       └────────┬────────┘
                                                   │
                                                   │ httpx (async)
                                                   │
                                          ┌────────▼────────┐
                                          │ Epstein Exposed  │
                                          │    Public API    │
                                          │ epsteinexposed   │
                                          │   .com/api       │
                                          └─────────────────┘
```

## Components

### `src/server.py` — MCP Server

The entrypoint. Defines the **FastMCP** server and registers four tools:

| Tool                  | Description                                      |
|-----------------------|--------------------------------------------------|
| `search_persons`      | Search persons by name (full or partial)         |
| `get_document`        | Retrieve a document by ID                        |
| `list_documents`      | List/filter documents with pagination            |
| `get_person_mentions` | Get all mentions of a person across documents    |

Each tool delegates to the `EpsteinClient`, serializes the response to JSON, and returns it as a string.

### `src/epstein_client.py` — HTTP Client

A thin **async** wrapper around the [Epstein Exposed REST API](https://epsteinexposed.com/api-docs).

Key design decisions:

- **Async context manager** — supports `async with EpsteinClient() as c:` for proper resource cleanup.
- **httpx-based** — non-blocking HTTP with connection pooling.
- **Fallback logic** — `get_person_mentions()` tries the `/mentions` endpoint first; if unavailable, falls back to person search.
- **Configurable base URL** — via the `EPSTEIN_API_BASE_URL` environment variable.

### `tests/` — Test Suite

| File               | Coverage                                          |
|--------------------|---------------------------------------------------|
| `test_client.py`   | Client lifecycle, all endpoints, edge cases, errors |
| `test_server.py`   | Tool registration, serialization, output format   |

Tests use **respx** to mock HTTP calls and **pytest-asyncio** for async test support.

## Data Flow

```
1. Agent sends tool call  →  MCP server receives via JSON-RPC
2. Server dispatches to   →  EpsteinClient method
3. Client fires HTTP GET  →  epsteinexposed.com/api/...
4. API response parsed    →  JSON serialized via _to_text()
5. Result returned        →  Agent receives tool output
```

## Error Handling

| Scenario                      | Behavior                                    |
|-------------------------------|---------------------------------------------|
| API returns 4xx/5xx           | `httpx.HTTPStatusError` raised              |
| `/mentions` unavailable       | Falls back to `search_persons`              |
| Non-serializable data         | `_to_text()` uses `str()` as fallback       |
| Client not closed             | Use `async with` or call `close()` manually |
