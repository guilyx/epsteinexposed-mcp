# Credits: Erwin Lejeune — 2026-02-23
"""Tests verifying the epsteinexposed package integration.

The package itself is fully tested in its own repo; here we verify the MCP
server's dependency works correctly in this context.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from epsteinexposed import AsyncEpsteinExposed, EpsteinExposedNotFoundError

BASE = "https://epsteinexposed.com/api/v1"
MOCK_TARGET = "curl_cffi.requests.AsyncSession.get"


@dataclass
class FakeResponse:
    status_code: int = 200
    _json: dict[str, Any] | None = None
    _text: str = ""
    headers: dict[str, str] = field(default_factory=dict)

    def json(self) -> Any:
        if self._json is not None:
            return self._json
        return json.loads(self._text)


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


@pytest.mark.asyncio
async def test_search_persons(client):
    with patch(MOCK_TARGET, new_callable=AsyncMock) as mock_get:
        mock_get.return_value = FakeResponse(
            _json=_envelope([{"id": 1, "name": "Test", "slug": "test"}])
        )
        result = await client.search_persons(q="Test")
    assert len(result.data) == 1
    assert result.data[0].name == "Test"


@pytest.mark.asyncio
async def test_get_person(client):
    with patch(MOCK_TARGET, new_callable=AsyncMock) as mock_get:
        mock_get.return_value = FakeResponse(
            _json={"data": {"id": 1, "name": "Bill Clinton", "slug": "bill-clinton", "bio": "42nd POTUS"}}
        )
        result = await client.get_person("bill-clinton")
    assert result.name == "Bill Clinton"


@pytest.mark.asyncio
async def test_get_person_not_found(client):
    with patch(MOCK_TARGET, new_callable=AsyncMock) as mock_get:
        mock_get.return_value = FakeResponse(status_code=404, _text="Not Found")
        with pytest.raises(EpsteinExposedNotFoundError):
            await client.get_person("nobody")


@pytest.mark.asyncio
async def test_search_documents(client):
    with patch(MOCK_TARGET, new_callable=AsyncMock) as mock_get:
        mock_get.return_value = FakeResponse(
            _json=_envelope([{"id": "d1", "title": "Deposition"}])
        )
        result = await client.search_documents(q="deposition")
    assert len(result.data) == 1


@pytest.mark.asyncio
async def test_search_flights(client):
    with patch(MOCK_TARGET, new_callable=AsyncMock) as mock_get:
        mock_get.return_value = FakeResponse(
            _json=_envelope([{
                "id": 1, "origin": "TIST", "passengerNames": ["A"],
                "passengerIds": [1], "passengerCount": 1,
            }])
        )
        result = await client.search_flights(passenger="A")
    assert result.data[0].origin == "TIST"


@pytest.mark.asyncio
async def test_cross_search(client):
    with patch(MOCK_TARGET, new_callable=AsyncMock) as mock_get:
        mock_get.return_value = FakeResponse(
            _json={
                "status": "ok",
                "documents": {"results": [{"id": "d1"}]},
                "emails": {"results": []},
            }
        )
        result = await client.search(q="wexner")
    assert len(result.documents.results) == 1
