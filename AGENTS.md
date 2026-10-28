# AGENTS.md

Guidance for AI coding agents (and humans) working on the **FindArtisan API**

## Project overview

- **Language**: Python 3.13
- **Framework**: FastAPI
- **Package manager**: `uv` (always use `uv`, never raw `pip`)
- **Layout**: `src/` layout with the `api` package

## Project structure

```
src/api/
├── main.py                # FastAPI app factory (create_app) + ASGI app + entry point
├── core/
│   ├── config.py         # Settings via pydantic-settings (loaded from .env)
│   ├── db.py             # Async engine, session factory, get_db dependency
│   └── security.py       # Password hashing (bcrypt) + JWT helpers
├── dependencies.py        # get_current_user (JWT bearer guard)
├── models/
│   ├── base.py           # Declarative Base (naming convention) + TimestampMixin
│   ├── user.py           # User model (single accounts table, Role enum)
│   └── artisan_profile.py# ArtisanProfile model (1:1 with users via user_id FK)
├── routers/
│   ├── auth.py           # /auth/register, /auth/login, /auth/me
│   └── health.py          # /health endpoint
└── schemas/
    └── user.py           # Pydantic request/response models per domain
migrations/                # Alembic (async template), env.py reads DATABASE_URL from Settings
tests/
└── test_health.py
```

## Model & migration conventions

- Models live in `src/api/models/` (one module per aggregate), all inheriting from
  `Base` in `models/base.py`; export every model from `models/__init__.py` so Alembic
  autogenerate sees them.
- Schema is always changed in two steps: update the SQLAlchemy models, then
  autogenerate a migration (`uv run alembic revision --autogenerate -m "..."`),
  review the generated file, and run `uv run alembic upgrade head` before committing.
- Never edit a migration that has already been applied/shared — add a new revision.
- Constraint naming comes from `NAMING_CONVENTION` in `models/base.py`; keep
  `target_metadata = Base.metadata` wiring in `migrations/env.py` intact.

## Common commands

```bash
uv sync                                  # install/sync dependencies
uv run uvicorn api.main:app --reload                # dev server on :8000
uv run find-artisan-api                  # dev server via project script
uv run pytest                            # run tests
uv run ruff check .                      # lint
uv run ruff check --fix .                # lint with autofix
uv run ruff format .                     # format
```

`uv.lock` must be committed whenever dependencies change. Do not edit it by hand.

## Code conventions

- Line length is 100 (ruff-configured). Keep code formatted with `ruff format`.
- Keep new endpoints in `src/api/routers/` (one module per domain, e.g. `artisans.py`, `requests.py`), registered in `create_app()` in `main.py`.
- Shared settings/constants belong in `core/config.py`; write business logic in `core/` or `services/` modules, not inside route handlers.
- Every domain router should use `tags=[...]` and typed responses (`response_model` or annotated return type).
- Every new endpoint needs a pytest test in `tests/` using `TestClient` from `api.main` (app factory), not hardcoded servers.
- App-level strings (project name, description, version) come from `Settings` — don't hardcode them in routers.
- Request/response schemas live in `src/api/schemas/` (pydantic), service/business
  logic in `src/api/services/`; route handlers stay thin (validate → call service → return).
- **Response envelope convention** — all data endpoints return JSON in the standard
  envelope (`schemas/response.py`):
  - success: `{"status": "success", "data": {...}}` — declare
    `response_model=SuccessEnvelope[<DataSchema>]` and return `SuccessEnvelope(data=...)`.
  - errors: `{"status": "error", "message": "...", "errors": [...]}` — never returned by
    hand; raise `HTTPException` / trigger validation and let the global handlers in
    `core/errors.py` render the envelope.
  - `/health` is exempt (load-balancer probe keeps its own shape).
- Endpoints requiring auth inject `get_current_user` from `api/dependencies.py`.
- Always upgrade away from deprecated packages/warnings — see "Dependency & deprecation policy" below.

## Definition of done

Before finishing any change, make sure:

1. `uv run pytest -W error::DeprecationWarning` passes (add/extend tests for new behavior).
2. `uv run ruff check .` and `uv run ruff format --check .` are clean.
3. The dev server still boots: `uv run uvicorn api.main:app` starts without errors.
4. New env vars are documented in `.env.example` and reflected in `core/config.py`.

## Dependency & deprecation policy

- **Always fix deprecation warnings from dependencies — never suppress or ignore them.**
  Migrate to the replacement the warning suggests instead of pinning the old package or
  silencing the warning with filters/`# noqa`.
- Example: the test suite once warned `StarletteDeprecationWarning: Using httpx with
  starlette.testclient is deprecated; install httpx2 instead` — the fix was to add
  `httpx2` and remove `httpx`, not to filter the warning.
- Keep the test suite warning-free. Run with `uv run pytest -W error::DeprecationWarning`
  so new deprecations fail the build immediately.

## Commit instructions

- Use **short conventional commit style**: `type(scope): description`.
- The description is lowercase, imperative, no trailing period, and kept short (ideally ≤ 72 characters total).
- Valid types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `build`, `ci`.
- The scope is optional but should name the touched domain or area (e.g. `api`, `health`, `config`, `deps`).
- Squash trivial housekeeping into related commits instead of separate `chore` noise.

### Examples

```
feat(artisans): add artisan profile model and router
fix(health): include version in health response
docs(readme): document nearby search endpoint
chore(deps): bump fastapi to 0.163
test(health): cover debug flag in health payload
```

### Examples of what to avoid

```
git commit -m "stuff"                              # no type/scope, not conventional
git commit -m "feat(artisans): Added The Artisan Profile Model And Router."  # too long, capitalized, period
```
