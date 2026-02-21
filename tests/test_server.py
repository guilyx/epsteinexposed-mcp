# Credits: Erwin Lejeune — 2026-02-21
"""Tests for the MCP server tools — ensures they serialize correctly."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from src.server import get_document, get_person_mentions, list_documents, search_persons


@pytest.mark.asyncio
async def test_search_persons_returns_json():
    mock_data = [{"name": "Test Person", "id": "1"}]
    with patch("src.server._client.search_persons", new_callable=AsyncMock, return_value=mock_data):
        result = await search_persons("Test")
    parsed = json.loads(result)
    assert parsed[0]["name"] == "Test Person"


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
    with patch("src.server._client.list_documents", new_callable=AsyncMock, return_value=mock_data):
        result = await list_documents(page=1, per_page=10)
    parsed = json.loads(result)
    assert len(parsed) == 2


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
