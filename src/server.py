# Credits: Erwin Lejeune — 2026-02-21
"""Epstein Files MCP Server — exposes Epstein Exposed API as MCP tools.

Run via:  python -m src.server          (stdio transport)
   or:    mcp run src/server.py         (using mcp CLI)
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.epstein_client import EpsteinClient

# ── MCP Server definition ─────────────────────────────────────
mcp = FastMCP(
    "Epstein Files",
    instructions="MCP server providing access to the Epstein Exposed public API — "
    "search persons, retrieve documents, and get mention context.",
)

_client = EpsteinClient()


def _to_text(data: Any) -> str:
    """Serialise an API response to readable text for the agent."""
    return json.dumps(data, indent=2, default=str)


# ── Tools ──────────────────────────────────────────────────────


@mcp.tool()
async def search_persons(name: str, page: int = 1, per_page: int = 50) -> str:
    """Search the Epstein files for a person by name.

    Args:
        name: The full or partial name to search for.
        page: Page number (default 1).
        per_page: Results per page (default 50).

    Returns:
        JSON string of matching person records.
    """
    result = await _client.search_persons(name, page=page, per_page=per_page)
    return _to_text(result)


@mcp.tool()
async def get_document(doc_id: str) -> str:
    """Retrieve a specific Epstein document by its ID.

    Args:
        doc_id: The unique identifier of the document.

    Returns:
        JSON string of the document contents and metadata.
    """
    result = await _client.get_document(doc_id)
    return _to_text(result)


@mcp.tool()
async def list_documents(
    page: int = 1,
    per_page: int = 50,
    category: str | None = None,
) -> str:
    """List available Epstein documents, optionally filtered by category.

    Args:
        page: Page number (default 1).
        per_page: Results per page (default 50).
        category: Optional category filter.

    Returns:
        JSON string of document listing with pagination info.
    """
    result = await _client.list_documents(page=page, per_page=per_page, category=category)
    return _to_text(result)


@mcp.tool()
async def get_person_mentions(name: str, page: int = 1, per_page: int = 50) -> str:
    """Get all mentions and contextual snippets for a person across Epstein documents.

    Args:
        name: The full or partial name to look up.
        page: Page number (default 1).
        per_page: Results per page (default 50).

    Returns:
        JSON string of document mentions with surrounding context.
    """
    result = await _client.get_person_mentions(name, page=page, per_page=per_page)
    return _to_text(result)


# ── Entrypoint ─────────────────────────────────────────────────


def main() -> None:
    """Run the MCP server via stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
