# Deploy with Docker

Run the MCP server in a Docker container for consistent, reproducible deployments.

## Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

EXPOSE 8000

# Default: stdio transport (for MCP clients)
CMD ["epsteinexposed-mcp"]
```

## Build & Run

```bash
# Build the image
docker build -t epsteinexposed-mcp .

# Run with stdio transport (pipe to MCP client)
docker run -i epsteinexposed-mcp

# Run with SSE transport (for HTTP-based clients)
docker run -p 8000:8000 epsteinexposed-mcp \
  python -c "from src.server import mcp; mcp.run(transport='sse', host='0.0.0.0', port=8000)"
```

## Environment Variables

Pass environment variables at runtime:

```bash
docker run -e EPSTEIN_API_BASE_URL=https://custom-api.example.com/api \
  -i epsteinexposed-mcp
```

## Docker Compose

If you're running this alongside other services (e.g., the LinkedStein backend):

```yaml
services:
  epstein-mcp:
    build: ./epsteinexposed-mcp
    environment:
      - EPSTEIN_API_BASE_URL=https://epsteinexposed.com/api
    stdin_open: true
    tty: true
```

## Health Check

For SSE transport deployments, add a health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s \
  CMD curl -f http://localhost:8000/health || exit 1
```
