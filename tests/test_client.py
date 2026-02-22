# Credits: Erwin Lejeune — 2026-02-22
"""Tests verifying the epsteinexposed package integration.

The package itself is fully tested in its own repo; here we verify the MCP
server's dependency works correctly in this context.
"""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from epsteinexposed import AsyncEpsteinExposed, EpsteinExposedNotFoundError

BASE = "https://epsteinexposed.com/api/v1"


def _envelope(data, total=None):
    return {
        "status": "ok",
        "data": data,
        "meta": {
            "total": total or len(data),
            "page": 1,
            "per_page": 20,
            "timestamp": "2026-02-22T00:00:00.000Z",
        },
    }


@pytest.fixture
async def client():
    async with AsyncEpsteinExposed(base_url=BASE) as c:
        yield c


@respx.mock
@pytest.mark.asyncio
async def test_search_persons(client):
    respx.get(f"{BASE}/persons").mock(
        return_value=Response(200, json=_envelope([{"id": 1, "name": "Test", "slug": "test"}]))
    )
    result = await client.search_persons(q="Test")
    assert len(result.data) == 1
    assert result.data[0].name == "Test"


@respx.mock
@pytest.mark.asyncio
async def test_get_person(client):
    respx.get(f"{BASE}/persons/bill-clinton").mock(
        return_value=Response(200, json={
            "data": {"id": 1, "name": "Bill Clinton", "slug": "bill-clinton", "bio": "42nd POTUS"}
        })
    )
    result = await client.get_person("bill-clinton")
    assert result.name == "Bill Clinton"


@respx.mock
@pytest.mark.asyncio
async def test_get_person_not_found(client):
    respx.get(f"{BASE}/persons/nobody").mock(return_value=Response(404))
    with pytest.raises(EpsteinExposedNotFoundError):
        await client.get_person("nobody")


@respx.mock
@pytest.mark.asyncio
async def test_search_documents(client):
    respx.get(f"{BASE}/documents").mock(
        return_value=Response(200, json=_envelope([{"id": "d1", "title": "Deposition"}]))
    )
    result = await client.search_documents(q="deposition")
    assert len(result.data) == 1


@respx.mock
@pytest.mark.asyncio
async def test_search_flights(client):
    respx.get(f"{BASE}/flights").mock(
        return_value=Response(200, json=_envelope([{
            "id": 1, "origin": "TIST", "passengerNames": ["A"], "passengerIds": [1],
            "passengerCount": 1,
        }]))
    )
    result = await client.search_flights(passenger="A")
    assert result.data[0].origin == "TIST"


@respx.mock
@pytest.mark.asyncio
async def test_cross_search(client):
    respx.get(f"{BASE}/search").mock(
        return_value=Response(200, json={
            "status": "ok",
            "documents": {"results": [{"id": "d1"}]},
            "emails": {"results": []},
        })
    )
    result = await client.search(q="wexner")
    assert len(result.documents.results) == 1
