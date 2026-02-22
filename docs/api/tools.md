# MCP Tools

The server exposes **four tools** via the Model Context Protocol. Each tool returns a JSON string.

---

## `search_persons`

Search the Epstein files for a person by name.

### Parameters

| Name       | Type   | Default | Description                          |
|------------|--------|---------|--------------------------------------|
| `name`     | `str`  | —       | Full or partial name to search for   |
| `page`     | `int`  | `1`     | Page number for pagination           |
| `per_page` | `int`  | `50`    | Results per page                     |

### Example Output

```json
[
  {
    "id": "p-1234",
    "name": "John Doe",
    "aliases": ["J. Doe"],
    "document_count": 12
  }
]
```

### API Endpoint

```
GET /persons?search={name}&page={page}&per_page={per_page}
```

---

## `get_document`

Retrieve a specific Epstein document by its ID.

### Parameters

| Name     | Type   | Default | Description                        |
|----------|--------|---------|------------------------------------|
| `doc_id` | `str`  | —       | Unique identifier of the document  |

### Example Output

```json
{
  "id": "doc-5678",
  "title": "Flight Log — January 2003",
  "category": "flight-logs",
  "pages": 4,
  "url": "https://epsteinexposed.com/documents/doc-5678"
}
```

### API Endpoint

```
GET /documents/{doc_id}
```

---

## `list_documents`

List available Epstein documents with optional category filter.

### Parameters

| Name       | Type          | Default | Description                        |
|------------|---------------|---------|------------------------------------|
| `page`     | `int`         | `1`     | Page number for pagination         |
| `per_page` | `int`         | `50`    | Results per page                   |
| `category` | `str \| None` | `None`  | Optional category filter           |

### Example Output

```json
[
  {
    "id": "doc-001",
    "title": "Deposition Transcript",
    "category": "depositions"
  },
  {
    "id": "doc-002",
    "title": "Flight Log",
    "category": "flight-logs"
  }
]
```

### API Endpoint

```
GET /documents?page={page}&per_page={per_page}&category={category}
```

---

## `get_person_mentions`

Get all mentions and contextual snippets for a person across Epstein documents.

### Parameters

| Name       | Type   | Default | Description                          |
|------------|--------|---------|--------------------------------------|
| `name`     | `str`  | —       | Full or partial name to look up      |
| `page`     | `int`  | `1`     | Page number for pagination           |
| `per_page` | `int`  | `50`    | Results per page                     |

### Example Output

```json
{
  "query": "John Doe",
  "results": [
    {
      "doc_id": "doc-5678",
      "doc_title": "Flight Log — January 2003",
      "context": "...passenger list included John Doe alongside..."
    }
  ]
}
```

### API Endpoint

```
GET /mentions?name={name}&page={page}&per_page={per_page}
```

::: tip Fallback Behavior
If the `/mentions` endpoint is unavailable (returns 4xx/5xx), the tool automatically falls back to `search_persons` and wraps the result in a `{"query": ..., "results": ...}` envelope.
:::
