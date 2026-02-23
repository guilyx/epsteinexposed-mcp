# Configuration

## Environment Variables

| Variable                 | Default                                | Description                              |
|--------------------------|----------------------------------------|------------------------------------------|
| `EPSTEIN_API_BASE_URL`   | `https://epsteinexposed.com/api`       | Base URL of the Epstein Exposed REST API |

### Example

```bash
# Override the API base URL (e.g., for a local proxy or staging)
export EPSTEIN_API_BASE_URL=http://localhost:8080/api
```

## Timeouts

The HTTP client uses a **30-second timeout** by default. This is hardcoded in `src/epstein_client.py`:

```python
_TIMEOUT = 30.0
```

To change it, modify the constant or subclass `EpsteinClient`.

## Transport Modes

The MCP server supports two transport modes:

### stdio (default)

```bash
python -m src.server
# or
epsteinexposed-mcp
```

Standard input/output — used by Claude Desktop, Cursor, and most MCP clients.

### SSE (Server-Sent Events)

If your client supports HTTP-based MCP, you can configure the server for SSE transport by modifying the `main()` function:

```python
def main() -> None:
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

## MCP Client Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "epstein-files": {
      "command": "epsteinexposed-mcp",
      "args": []
    }
  }
}
```

### Cursor

Add to your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "epstein-files": {
      "command": "epsteinexposed-mcp",
      "args": []
    }
  }
}
```

### SmolAgents / Custom

```python
from smolagents import ToolCollection
from mcp import StdioServerParameters

server_params = StdioServerParameters(
    command="epsteinexposed-mcp",
    args=[],
)

with ToolCollection.from_mcp(server_params) as tools:
    # Use tools in your agent
    pass
```
