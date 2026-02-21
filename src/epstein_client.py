# Credits: Erwin Lejeune — 2026-02-21
"""HTTP client wrapping the Epstein Exposed REST API (https://epsteinexposed.com/api-docs)."""

from __future__ import annotations

import os
from typing import Any

import httpx

BASE_URL = os.getenv("EPSTEIN_API_BASE_URL", "https://epsteinexposed.com/api")
_TIMEOUT = 30.0


class EpsteinClient:
    """Thin async wrapper around the Epstein Exposed public API."""

    def __init__(self, base_url: str = BASE_URL) -> None:
        self._base = base_url.rstrip("/")
        self._http = httpx.AsyncClient(timeout=_TIMEOUT, base_url=self._base)

    async def close(self) -> None:
        await self._http.aclose()

    # ── Persons ────────────────────────────────────────────────

    async def search_persons(self, name: str, page: int = 1, per_page: int = 50) -> dict[str, Any]:
        """Search the Epstein files for a person by name.

        Expected endpoint: GET /persons?search=<name>&page=<n>&per_page=<n>
        """
        resp = await self._http.get(
            "/persons",
            params={"search": name, "page": page, "per_page": per_page},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_person(self, person_id: str) -> dict[str, Any]:
        """Fetch a single person by ID.

        Expected endpoint: GET /persons/<id>
        """
        resp = await self._http.get(f"/persons/{person_id}")
        resp.raise_for_status()
        return resp.json()

    async def list_persons(self, page: int = 1, per_page: int = 100) -> dict[str, Any]:
        """List all persons (paginated).

        Expected endpoint: GET /persons?page=<n>&per_page=<n>
        """
        resp = await self._http.get(
            "/persons",
            params={"page": page, "per_page": per_page},
        )
        resp.raise_for_status()
        return resp.json()

    # ── Documents ──────────────────────────────────────────────

    async def get_document(self, doc_id: str) -> dict[str, Any]:
        """Retrieve a specific document by ID.

        Expected endpoint: GET /documents/<id>
        """
        resp = await self._http.get(f"/documents/{doc_id}")
        resp.raise_for_status()
        return resp.json()

    async def list_documents(
        self,
        page: int = 1,
        per_page: int = 50,
        category: str | None = None,
    ) -> dict[str, Any]:
        """List / filter documents.

        Expected endpoint: GET /documents?page=<n>&per_page=<n>&category=<cat>
        """
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if category:
            params["category"] = category
        resp = await self._http.get("/documents", params=params)
        resp.raise_for_status()
        return resp.json()

    # ── Mentions / Context ─────────────────────────────────────

    async def get_person_mentions(
        self, name: str, page: int = 1, per_page: int = 50
    ) -> dict[str, Any]:
        """Get all document mentions / context for a given person name.

        Expected endpoint: GET /mentions?name=<name>&page=<n>&per_page=<n>
        Falls back to person search + document fetch if /mentions is not available.
        """
        try:
            resp = await self._http.get(
                "/mentions",
                params={"name": name, "page": page, "per_page": per_page},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError:
            # Fallback: use person search
            persons = await self.search_persons(name, page=page, per_page=per_page)
            return {"query": name, "results": persons}
