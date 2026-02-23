# Credits: Erwin Lejeune — 2026-02-22
"""Epstein Files MCP Server — exposes Epstein Exposed API as MCP tools.

Powered by the `epsteinexposed` Python client library.

Run via:  python -m src.server          (stdio transport)
   or:    mcp run src/server.py         (using mcp CLI)
"""

from __future__ import annotations

import json
from typing import Any

from epsteinexposed import AsyncEpsteinExposed
from mcp.server.fastmcp import FastMCP

# ── MCP Server definition ─────────────────────────────────────
mcp = FastMCP(
    "Epstein Files",
    instructions="MCP server providing full access to the Epstein Exposed public API — "
    "search persons, get person detail, search documents, search flight logs, "
    "and cross-type search across documents and emails.",
)

_client = AsyncEpsteinExposed()


def _to_text(data: Any) -> str:
    """Serialise an API response to readable text for the agent."""
    return json.dumps(data, indent=2, default=str)


def _dump_paginated(resp: Any) -> str:
    """Serialize a PaginatedResponse to JSON."""
    return _to_text(
        {
            "status": resp.status,
            "data": [item.model_dump(by_alias=True) for item in resp.data],
            "meta": resp.meta.model_dump(),
        }
    )


# ── Person Tools ──────────────────────────────────────────────


@mcp.tool()
async def search_persons(
    name: str | None = None,
    category: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> str:
    """Search the Epstein files for persons of interest.

    Args:
        name: Full or partial name to search for.
        category: Filter by category (politician, business, royalty, celebrity,
                  associate, legal, academic, socialite, military-intelligence, other).
        page: Page number (default 1).
        per_page: Results per page, max 100 (default 20).

    Returns:
        JSON with matching person records including stats (flights, documents, etc.).
    """
    result = await _client.search_persons(q=name, category=category, page=page, per_page=per_page)
    return _dump_paginated(result)


@mcp.tool()
async def get_person(slug: str) -> str:
    """Get full detail for a specific person by their URL slug.

    Returns biographical info, aliases, black book entry status, and aggregate stats
    (flights, documents, connections, emails).

    Args:
        slug: The person's URL slug (e.g. "bill-clinton", "ghislaine-maxwell").

    Returns:
        JSON with full person detail.
    """
    result = await _client.get_person(slug)
    return _to_text(result.model_dump(by_alias=True))


# ── Document Tools ────────────────────────────────────────────


@mcp.tool()
async def search_documents(
    query: str | None = None,
    source: str | None = None,
    category: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> str:
    """Search Epstein case documents using full-text search (FTS5).

    Args:
        query: Full-text search query (e.g. "little st james", "flight log").
        source: Filter by document source (court-filing, doj-release, fbi, efta).
        category: Filter by document category (deposition, testimony, correspondence).
        page: Page number (default 1).
        per_page: Results per page, max 100 (default 20).

    Returns:
        JSON with matching documents including title, date, source, summary, tags.
    """
    result = await _client.search_documents(
        q=query, source=source, category=category, page=page, per_page=per_page
    )
    return _dump_paginated(result)


# ── Flight Tools ──────────────────────────────────────────────


@mcp.tool()
async def search_flights(
    passenger: str | None = None,
    year: int | None = None,
    origin: str | None = None,
    destination: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> str:
    """Search Epstein's flight logs (~1997-2006) across all known aircraft.

    Args:
        passenger: Filter by passenger name.
        year: Filter by year (e.g. 2002).
        origin: Filter by departure location (e.g. "TIST", "Palm Beach").
        destination: Filter by arrival location (e.g. "Teterboro", "CYUL").
        page: Page number (default 1).
        per_page: Results per page, max 100 (default 20).

    Returns:
        JSON with flight records including date, route, aircraft, pilot, and passengers.
    """
    result = await _client.search_flights(
        passenger=passenger,
        year=year,
        origin=origin,
        destination=destination,
        page=page,
        per_page=per_page,
    )
    return _dump_paginated(result)


# ── Cross-type Search ─────────────────────────────────────────


@mcp.tool()
async def cross_search(
    query: str,
    type: str | None = None,
    limit: int = 20,
) -> str:
    """Search across documents AND emails simultaneously using full-text search.

    Args:
        query: Search query (required).
        type: Limit to "documents" or "emails". Omit to search both.
        limit: Max results per type, max 100 (default 20).

    Returns:
        JSON with separate result arrays for documents and emails.
    """
    result = await _client.search(q=query, type=type, limit=limit)
    return _to_text(result.model_dump())


# ── Entrypoint ─────────────────────────────────────────────────


def main() -> None:
    """Run the MCP server via stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
