# Credits: Erwin Lejeune — 2026-02-22
"""Tests for the MCP server tools backed by epsteinexposed."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from epsteinexposed.models import (
    Document,
    Flight,
    PaginatedResponse,
    PaginationMeta,
    Person,
    PersonDetail,
    PersonStats,
    SearchResults,
)

from src.server import (
    _to_text,
    cross_search,
    get_person,
    mcp,
    search_documents,
    search_flights,
    search_persons,
)

# ── Helper tests ──────────────────────────────────────────────


class TestToText:
    def test_dict(self):
        assert json.loads(_to_text({"key": "value"})) == {"key": "value"}

    def test_list(self):
        assert json.loads(_to_text([1, 2, 3])) == [1, 2, 3]

    def test_nested(self):
        data = {"persons": [{"name": "A", "docs": [1, 2]}]}
        assert json.loads(_to_text(data)) == data

    def test_non_serializable_uses_str(self):
        import datetime

        result = _to_text({"date": datetime.date(2026, 1, 1)})
        parsed = json.loads(result)
        assert parsed["date"] == "2026-01-01"


# ── Tool registration ────────────────────────────────────────


class TestToolRegistration:
    def test_mcp_server_name(self):
        assert mcp.name == "Epstein Files"

    def test_search_persons_registered(self):
        tools = mcp._tool_manager._tools
        assert "search_persons" in tools

    def test_get_person_registered(self):
        tools = mcp._tool_manager._tools
        assert "get_person" in tools

    def test_search_documents_registered(self):
        tools = mcp._tool_manager._tools
        assert "search_documents" in tools

    def test_search_flights_registered(self):
        tools = mcp._tool_manager._tools
        assert "search_flights" in tools

    def test_cross_search_registered(self):
        tools = mcp._tool_manager._tools
        assert "cross_search" in tools

    def test_total_tool_count(self):
        tools = mcp._tool_manager._tools
        assert len(tools) == 5


# ── Persons ───────────────────────────────────────────────────


def _paginated_persons(data: list[dict]) -> PaginatedResponse[Person]:
    return PaginatedResponse[Person](
        status="ok",
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=20),
    )


@pytest.mark.asyncio
async def test_search_persons_returns_json():
    mock = _paginated_persons([{"id": 1, "name": "Test Person", "slug": "test"}])
    with patch("src.server._client.search_persons", new_callable=AsyncMock, return_value=mock):
        result = await search_persons("Test")
    parsed = json.loads(result)
    assert parsed["data"][0]["name"] == "Test Person"


@pytest.mark.asyncio
async def test_search_persons_with_category():
    mock = _paginated_persons([])
    with patch(
        "src.server._client.search_persons", new_callable=AsyncMock, return_value=mock
    ) as fn:
        await search_persons("X", category="politician")
    fn.assert_called_once_with(q="X", category="politician", page=1, per_page=20)


@pytest.mark.asyncio
async def test_get_person_returns_json():
    mock = PersonDetail(
        id=1,
        name="Jane Smith",
        slug="jane-smith",
        bio="A person",
        aliases=["J. Smith"],
        black_book_entry=True,
        stats=PersonStats(flights=5, documents=10, connections=3, emails=2),
    )
    with patch("src.server._client.get_person", new_callable=AsyncMock, return_value=mock):
        result = await get_person("jane-smith")
    parsed = json.loads(result)
    assert parsed["name"] == "Jane Smith"
    assert parsed["blackBookEntry"] is True
    assert parsed["stats"]["flights"] == 5


# ── Documents ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_documents_returns_json():
    mock = PaginatedResponse[Document](
        status="ok",
        data=[{"id": "d1", "title": "Flight Log"}],
        meta=PaginationMeta(total=1),
    )
    with patch("src.server._client.search_documents", new_callable=AsyncMock, return_value=mock):
        result = await search_documents(query="flight")
    parsed = json.loads(result)
    assert parsed["data"][0]["title"] == "Flight Log"


@pytest.mark.asyncio
async def test_search_documents_with_filters():
    mock = PaginatedResponse[Document](status="ok", data=[], meta=PaginationMeta())
    with patch(
        "src.server._client.search_documents", new_callable=AsyncMock, return_value=mock
    ) as fn:
        await search_documents(query="test", source="fbi", category="deposition")
    fn.assert_called_once_with(q="test", source="fbi", category="deposition", page=1, per_page=20)


# ── Flights ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_flights_returns_json():
    mock = PaginatedResponse[Flight](
        status="ok",
        data=[
            {
                "id": 1,
                "date": "2002-01-15",
                "origin": "Palm Beach",
                "destination": "Teterboro",
                "passengerNames": ["A"],
                "passengerIds": [1],
                "passengerCount": 1,
            }
        ],
        meta=PaginationMeta(total=1),
    )
    with patch("src.server._client.search_flights", new_callable=AsyncMock, return_value=mock):
        result = await search_flights(passenger="A")
    parsed = json.loads(result)
    assert parsed["data"][0]["origin"] == "Palm Beach"


@pytest.mark.asyncio
async def test_search_flights_with_filters():
    mock = PaginatedResponse[Flight](status="ok", data=[], meta=PaginationMeta())
    with patch(
        "src.server._client.search_flights", new_callable=AsyncMock, return_value=mock
    ) as fn:
        await search_flights(year=2003, origin="TIST")
    fn.assert_called_once_with(
        passenger=None, year=2003, origin="TIST", destination=None, page=1, per_page=20
    )


# ── Cross-type Search ────────────────────────────────────────


@pytest.mark.asyncio
async def test_cross_search_returns_json():
    mock = SearchResults(
        status="ok",
        documents={"results": [{"id": "d1", "title": "T"}]},
        emails={"results": []},
    )
    with patch("src.server._client.search", new_callable=AsyncMock, return_value=mock):
        result = await cross_search(query="wexner")
    parsed = json.loads(result)
    assert len(parsed["documents"]["results"]) == 1
    assert parsed["emails"]["results"] == []


@pytest.mark.asyncio
async def test_cross_search_with_type():
    mock = SearchResults(status="ok")
    with patch("src.server._client.search", new_callable=AsyncMock, return_value=mock) as fn:
        await cross_search(query="test", type="documents", limit=10)
    fn.assert_called_once_with(q="test", type="documents", limit=10)
