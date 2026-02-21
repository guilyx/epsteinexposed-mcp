# HTTP Client

The `EpsteinClient` class is a thin async wrapper around the Epstein Exposed REST API. You can use it standalone, outside of the MCP server context.

## Import

```python
from src.epstein_client import EpsteinClient
```

## Usage

### As an async context manager (recommended)

```python
async with EpsteinClient() as client:
    results = await client.search_persons("Doe")
    doc = await client.get_document("doc-123")
```

### Manual lifecycle

```python
client = EpsteinClient()
try:
    results = await client.search_persons("Smith")
finally:
    await client.close()
```

## Constructor

```python
EpsteinClient(base_url: str = BASE_URL)
```

| Parameter  | Type   | Default                                  | Description            |
|------------|--------|------------------------------------------|------------------------|
| `base_url` | `str`  | `EPSTEIN_API_BASE_URL` env or fallback   | API base URL           |

## Methods

### `search_persons(name, page=1, per_page=50)`

Search for persons by name.

**Returns:** `dict[str, Any]`

---

### `get_person(person_id)`

Fetch a single person by ID.

**Returns:** `dict[str, Any]`

**Raises:** `httpx.HTTPStatusError` if not found.

---

### `list_persons(page=1, per_page=100)`

List all persons with pagination.

**Returns:** `dict[str, Any]`

---

### `get_document(doc_id)`

Retrieve a document by ID.

**Returns:** `dict[str, Any]`

**Raises:** `httpx.HTTPStatusError` if not found.

---

### `list_documents(page=1, per_page=50, category=None)`

List documents with optional category filter.

**Returns:** `dict[str, Any]`

---

### `get_person_mentions(name, page=1, per_page=50)`

Get document mentions for a person. Falls back to `search_persons` if the `/mentions` endpoint is unavailable.

**Returns:** `dict[str, Any]`

---

### `close()`

Close the underlying HTTP transport. Called automatically when using `async with`.
