# Credits: Erwin Lejeune — 2026-02-21
"""Tests for the MCP server tools — ensures they serialize correctly."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from src.server import (
    _to_text,
    get_document,
    get_person_mentions,
    list_documents,
    mcp,
    search_persons,
)


# ── Helper tests ──────────────────────────────────────────────


class TestToText:
    """Tests for the _to_text serialization helper."""

    def test_dict(self):
        assert json.loads(_to_text({"key": "value"})) == {"key": "value"}

    def test_list(self):
        assert json.loads(_to_text([1, 2, 3])) == [1, 2, 3]

    def test_nested(self):
        data = {"persons": [{"name": "A", "docs": [1, 2]}]}
        assert json.loads(_to_text(data)) == data

    def test_non_serializable_uses_str(self):
        """Non-JSON-serializable objects should be converted via str()."""
        import datetime

        result = _to_text({"date": datetime.date(2026, 1, 1)})
        parsed = json.loads(result)
        assert parsed["date"] == "2026-01-01"

    def test_empty_dict(self):
        assert json.loads(_to_text({})) == {}

    def test_none_value(self):
        assert json.loads(_to_text({"key": None})) == {"key": None}


# ── Tool registration ────────────────────────────────────────


class TestToolRegistration:
    """Verify that all expected tools are registered on the MCP server."""

    def test_mcp_server_name(self):
        assert mcp.name == "Epstein Files"

    def test_search_persons_registered(self):
        tools = mcp._tool_manager._tools
        assert "search_persons" in tools

    def test_get_document_registered(self):
        tools = mcp._tool_manager._tools
        assert "get_document" in tools

    def test_list_documents_registered(self):
        tools = mcp._tool_manager._tools
        assert "list_documents" in tools

    def test_get_person_mentions_registered(self):
        tools = mcp._tool_manager._tools
        assert "get_person_mentions" in tools

    def test_total_tool_count(self):
        """Exactly 4 tools should be exposed."""
        tools = mcp._tool_manager._tools
        assert len(tools) == 4


# ── Tool output tests ────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_persons_returns_json():
    mock_data = [{"name": "Test Person", "id": "1"}]
    with patch("src.server._client.search_persons", new_callable=AsyncMock, return_value=mock_data):
        result = await search_persons("Test")
    parsed = json.loads(result)
    assert parsed[0]["name"] == "Test Person"


@pytest.mark.asyncio
async def test_search_persons_with_pagination():
    mock_data = {"results": [], "page": 2, "total": 0}
    with patch("src.server._client.search_persons", new_callable=AsyncMock, return_value=mock_data):
        result = await search_persons("Nobody", page=2, per_page=10)
    parsed = json.loads(result)
    assert parsed["page"] == 2


@pytest.mark.asyncio
async def test_get_document_returns_json():
    mock_data = {"id": "doc-1", "title": "Test Doc"}
    with patch("src.server._client.get_document", new_callable=AsyncMock, return_value=mock_data):
        result = await get_document("doc-1")
    parsed = json.loads(result)
    assert parsed["title"] == "Test Doc"


@pytest.mark.asyncio
async def test_list_documents_returns_json():
    mock_data = [{"id": "d1"}, {"id": "d2"}]
    with patch(
        "src.server._client.list_documents", new_callable=AsyncMock, return_value=mock_data
    ):
        result = await list_documents(page=1, per_page=10)
    parsed = json.loads(result)
    assert len(parsed) == 2


@pytest.mark.asyncio
async def test_list_documents_with_category():
    mock_data = [{"id": "d1", "category": "legal"}]
    with patch(
        "src.server._client.list_documents", new_callable=AsyncMock, return_value=mock_data
    ) as mock_fn:
        result = await list_documents(page=1, per_page=10, category="legal")
    mock_fn.assert_called_once_with(page=1, per_page=10, category="legal")
    parsed = json.loads(result)
    assert parsed[0]["category"] == "legal"


@pytest.mark.asyncio
async def test_get_person_mentions_returns_json():
    mock_data = {"query": "John", "results": [{"doc_id": "d1"}]}
    with patch(
        "src.server._client.get_person_mentions",
        new_callable=AsyncMock,
        return_value=mock_data,
    ):
        result = await get_person_mentions("John")
    parsed = json.loads(result)
    assert parsed["query"] == "John"


@pytest.mark.asyncio
async def test_search_persons_empty_result():
    """Tool should still produce valid JSON for empty results."""
    with patch("src.server._client.search_persons", new_callable=AsyncMock, return_value=[]):
        result = await search_persons("NoMatch")
    parsed = json.loads(result)
    assert parsed == []
