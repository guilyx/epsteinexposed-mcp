# Credits: Erwin Lejeune — 2026-02-21
"""Tests for the EpsteinClient HTTP wrapper."""

from __future__ import annotations

import httpx
import pytest
import respx
from httpx import Response

from src.epstein_client import EpsteinClient

BASE = "https://epsteinexposed.com/api"


@pytest.fixture()
def client():
    return EpsteinClient(base_url=BASE)


@respx.mock
@pytest.mark.asyncio
async def test_search_persons(client: EpsteinClient):
    mock_data = [{"name": "John Doe", "id": "1"}]
    respx.get(f"{BASE}/persons").mock(return_value=Response(200, json=mock_data))

    result = await client.search_persons("John")
    assert result == mock_data


@respx.mock
@pytest.mark.asyncio
async def test_get_person(client: EpsteinClient):
    mock_data = {"name": "Jane Smith", "id": "42"}
    respx.get(f"{BASE}/persons/42").mock(return_value=Response(200, json=mock_data))

    result = await client.get_person("42")
    assert result["name"] == "Jane Smith"


@respx.mock
@pytest.mark.asyncio
async def test_list_persons(client: EpsteinClient):
    mock_data = {"results": [{"name": "A"}, {"name": "B"}]}
    respx.get(f"{BASE}/persons").mock(return_value=Response(200, json=mock_data))

    result = await client.list_persons(page=1, per_page=10)
    assert "results" in result


@respx.mock
@pytest.mark.asyncio
async def test_get_document(client: EpsteinClient):
    mock_data = {"id": "doc-1", "title": "Flight Log"}
    respx.get(f"{BASE}/documents/doc-1").mock(return_value=Response(200, json=mock_data))

    result = await client.get_document("doc-1")
    assert result["title"] == "Flight Log"


@respx.mock
@pytest.mark.asyncio
async def test_list_documents(client: EpsteinClient):
    mock_data = [{"id": "doc-1"}, {"id": "doc-2"}]
    respx.get(f"{BASE}/documents").mock(return_value=Response(200, json=mock_data))

    result = await client.list_documents()
    assert len(result) == 2


@respx.mock
@pytest.mark.asyncio
async def test_list_documents_with_category(client: EpsteinClient):
    mock_data = [{"id": "doc-3", "category": "legal"}]
    respx.get(f"{BASE}/documents").mock(return_value=Response(200, json=mock_data))

    result = await client.list_documents(category="legal")
    assert len(result) == 1


@respx.mock
@pytest.mark.asyncio
async def test_get_person_mentions(client: EpsteinClient):
    mock_data = {"query": "John", "results": []}
    respx.get(f"{BASE}/mentions").mock(return_value=Response(200, json=mock_data))

    result = await client.get_person_mentions("John")
    assert result["query"] == "John"


@respx.mock
@pytest.mark.asyncio
async def test_get_person_mentions_fallback(client: EpsteinClient):
    """When /mentions returns 404, should fall back to search_persons."""
    respx.get(f"{BASE}/mentions").mock(return_value=Response(404))
    mock_persons = [{"name": "John Doe"}]
    respx.get(f"{BASE}/persons").mock(return_value=Response(200, json=mock_persons))

    result = await client.get_person_mentions("John")
    assert "results" in result


@respx.mock
@pytest.mark.asyncio
async def test_search_persons_http_error(client: EpsteinClient):
    respx.get(f"{BASE}/persons").mock(return_value=Response(500))

    with pytest.raises(httpx.HTTPStatusError):
        await client.search_persons("test")
