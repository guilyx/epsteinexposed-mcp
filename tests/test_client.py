# Credits: Erwin Lejeune — 2026-02-21
"""Tests for the EpsteinClient HTTP wrapper."""

from __future__ import annotations

import os
from unittest.mock import patch

import httpx
import pytest
import respx
from httpx import Response

from src.epstein_client import BASE_URL, EpsteinClient

BASE = "https://epsteinexposed.com/api"


@pytest.fixture()
def client():
    return EpsteinClient(base_url=BASE)


# ── Construction / lifecycle ──────────────────────────────────


def test_default_base_url():
    """Client should use the EPSTEIN_API_BASE_URL env var by default."""
    c = EpsteinClient()
    assert c._base == BASE_URL.rstrip("/")


def test_custom_base_url():
    """Trailing slash should be stripped."""
    c = EpsteinClient(base_url="https://example.com/v2/")
    assert c._base == "https://example.com/v2"


def test_env_var_override():
    """EPSTEIN_API_BASE_URL env var should be picked up at import time."""
    # BASE_URL is evaluated at module import, so we test the constructor accepts it
    c = EpsteinClient(base_url="https://custom.api/ep")
    assert c._base == "https://custom.api/ep"


@pytest.mark.asyncio
async def test_context_manager():
    """Client should work as an async context manager."""
    async with EpsteinClient(base_url=BASE) as c:
        assert c._base == BASE
    # After exit, the client should have been closed
    assert c._http.is_closed


@pytest.mark.asyncio
async def test_close(client: EpsteinClient):
    """Explicit close should shut down the HTTP transport."""
    await client.close()
    assert client._http.is_closed


# ── Persons ───────────────────────────────────────────────────


@respx.mock
@pytest.mark.asyncio
async def test_search_persons(client: EpsteinClient):
    mock_data = [{"name": "John Doe", "id": "1"}]
    respx.get(f"{BASE}/persons").mock(return_value=Response(200, json=mock_data))

    result = await client.search_persons("John")
    assert result == mock_data


@respx.mock
@pytest.mark.asyncio
async def test_search_persons_params(client: EpsteinClient):
    """Verify query parameters are forwarded correctly."""
    route = respx.get(f"{BASE}/persons").mock(return_value=Response(200, json=[]))

    await client.search_persons("Doe", page=3, per_page=25)

    assert route.called
    request = route.calls.last.request
    assert request.url.params["search"] == "Doe"
    assert request.url.params["page"] == "3"
    assert request.url.params["per_page"] == "25"


@respx.mock
@pytest.mark.asyncio
async def test_search_persons_empty_results(client: EpsteinClient):
    """Empty result set should return an empty list."""
    respx.get(f"{BASE}/persons").mock(return_value=Response(200, json=[]))

    result = await client.search_persons("NonExistentName12345")
    assert result == []


@respx.mock
@pytest.mark.asyncio
async def test_search_persons_special_characters(client: EpsteinClient):
    """Names with special characters should be URL-encoded properly."""
    route = respx.get(f"{BASE}/persons").mock(return_value=Response(200, json=[]))

    await client.search_persons("O'Brien-Smith")

    request = route.calls.last.request
    assert "O%27Brien-Smith" in str(request.url) or "O'Brien-Smith" in str(request.url.params)


@respx.mock
@pytest.mark.asyncio
async def test_get_person(client: EpsteinClient):
    mock_data = {"name": "Jane Smith", "id": "42"}
    respx.get(f"{BASE}/persons/42").mock(return_value=Response(200, json=mock_data))

    result = await client.get_person("42")
    assert result["name"] == "Jane Smith"


@respx.mock
@pytest.mark.asyncio
async def test_get_person_not_found(client: EpsteinClient):
    """404 for a missing person should raise HTTPStatusError."""
    respx.get(f"{BASE}/persons/9999").mock(return_value=Response(404))

    with pytest.raises(httpx.HTTPStatusError):
        await client.get_person("9999")


@respx.mock
@pytest.mark.asyncio
async def test_list_persons(client: EpsteinClient):
    mock_data = {"results": [{"name": "A"}, {"name": "B"}]}
    respx.get(f"{BASE}/persons").mock(return_value=Response(200, json=mock_data))

    result = await client.list_persons(page=1, per_page=10)
    assert "results" in result


@respx.mock
@pytest.mark.asyncio
async def test_list_persons_pagination(client: EpsteinClient):
    """Verify pagination params are forwarded."""
    route = respx.get(f"{BASE}/persons").mock(return_value=Response(200, json={}))

    await client.list_persons(page=5, per_page=20)

    request = route.calls.last.request
    assert request.url.params["page"] == "5"
    assert request.url.params["per_page"] == "20"


# ── Documents ─────────────────────────────────────────────────


@respx.mock
@pytest.mark.asyncio
async def test_get_document(client: EpsteinClient):
    mock_data = {"id": "doc-1", "title": "Flight Log"}
    respx.get(f"{BASE}/documents/doc-1").mock(return_value=Response(200, json=mock_data))

    result = await client.get_document("doc-1")
    assert result["title"] == "Flight Log"


@respx.mock
@pytest.mark.asyncio
async def test_get_document_not_found(client: EpsteinClient):
    """404 for a missing document should raise HTTPStatusError."""
    respx.get(f"{BASE}/documents/missing").mock(return_value=Response(404))

    with pytest.raises(httpx.HTTPStatusError):
        await client.get_document("missing")


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
    """Category param should be passed when provided."""
    route = respx.get(f"{BASE}/documents").mock(
        return_value=Response(200, json=[{"id": "doc-3", "category": "legal"}])
    )

    result = await client.list_documents(category="legal")

    assert len(result) == 1
    request = route.calls.last.request
    assert request.url.params["category"] == "legal"


@respx.mock
@pytest.mark.asyncio
async def test_list_documents_without_category(client: EpsteinClient):
    """Category param should NOT be sent when None."""
    route = respx.get(f"{BASE}/documents").mock(return_value=Response(200, json=[]))

    await client.list_documents(category=None)

    request = route.calls.last.request
    assert "category" not in request.url.params


# ── Mentions / Context ────────────────────────────────────────


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
    assert result["query"] == "John"


@respx.mock
@pytest.mark.asyncio
async def test_get_person_mentions_fallback_on_500(client: EpsteinClient):
    """Server error on /mentions should also trigger fallback."""
    respx.get(f"{BASE}/mentions").mock(return_value=Response(500))
    respx.get(f"{BASE}/persons").mock(return_value=Response(200, json=[]))

    result = await client.get_person_mentions("Jane")
    assert result["query"] == "Jane"


# ── Error handling ────────────────────────────────────────────


@respx.mock
@pytest.mark.asyncio
async def test_search_persons_http_error(client: EpsteinClient):
    respx.get(f"{BASE}/persons").mock(return_value=Response(500))

    with pytest.raises(httpx.HTTPStatusError):
        await client.search_persons("test")


@respx.mock
@pytest.mark.asyncio
async def test_list_documents_server_error(client: EpsteinClient):
    """503 from the API should propagate as HTTPStatusError."""
    respx.get(f"{BASE}/documents").mock(return_value=Response(503))

    with pytest.raises(httpx.HTTPStatusError):
        await client.list_documents()
