# FindArtisan API

FastAPI backend for **FindArtisan** — a solution that helps clients find skilled artisans nearby and request their services.

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/) package manager

## Getting started

```bash
# Install dependencies (creates .venv automatically)
uv sync

# Run the development server
uv run uvicorn api.main:app --reload

# Or via the project script (development server on port 8000)
uv run find-artisan-api
```

The API is now available at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Health check: <http://localhost:8000/health>

## Configuration

Copy `.env.example` to `.env` and adjust values. Settings are loaded via pydantic-settings in
`api/core/config.py`.

## Testing & linting

```bash
uv run pytest       # run tests
uv run ruff check . # lint
uv run ruff format . # format
```

## Project structure

```
src/api/
├── __init__.py
├── main.py                # FastAPI app factory + entry point
├── core/
│   └── config.py          # Settings (pydantic-settings)
└── routers/
    └── health.py          # /health endpoint
tests/
└── test_health.py
```

## Roadmap

Planned FindArtisan features (not yet implemented):

- Client & artisan accounts and authentication
- Artisan profiles with skills, trade categories, and locations
- Nearby artisan search
- Service requests, quotes, and booking
- Reviews and ratings
