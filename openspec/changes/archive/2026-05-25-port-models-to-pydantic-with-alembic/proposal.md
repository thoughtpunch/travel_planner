## Why

Today `app/models.py` uses **SQLModel** — a library that mashes a
Pydantic schema and a SQLAlchemy ORM model into one class. SQLModel is
fine for tiny projects, but it's biting us in three places:

1. **Schema duality leaks.** `app/schemas.py` already maintains pure
   Pydantic IO models (`ConfigPayload`, `RunOut`, `ItineraryOut`, …),
   and `app/models.py` re-states the same fields in a SQLModel hybrid.
   Some fields get duplicated; some drift (e.g. `Leg.return_*` exist
   on the table but the schema mirror only added them later). One
   discipline (Pydantic for IO, SQLAlchemy for DB) makes the boundary
   obvious.
2. **No migrations.** `db.py:init_db()` calls
   `SQLModel.metadata.create_all(engine)` on every boot. The Phase-1
   schema has already evolved (added `Leg.return_date_anchor`,
   `Fare.return_date`, etc.) and we got lucky because the dev DB is
   throwaway. For any deploy that retains a DB across versions —
   including upgrading a friend or two onto this app — we need real
   schema migrations. Alembic is the standard.
3. **Async/threading friction.** SQLModel's sessions follow the same
   threading rules as SQLAlchemy, but the project already adds
   `check_same_thread=False` and runs the runner on a manually-spawned
   thread (`api/runs.py:65`). Owning the SQLAlchemy session lifecycle
   explicitly (`Session`, `sessionmaker`) will make future async or
   process-isolated work cleaner.

## What Changes

- **Models.** Replace SQLModel classes in `app/models.py` with
  SQLAlchemy 2.0 declarative `Mapped`/`mapped_column` ORM classes.
  Keep the same table names (`config`, `leg`, `run`, `fare`,
  `itinerary`) and column shapes so the DB-on-disk is wire-compatible.
- **Schemas.** Promote `app/schemas.py` to the single home for Pydantic
  IO models. Add `ConfigIn`, `LegIn`, etc., distinct from the ORM
  classes. Implement explicit `from_orm`-style adapters
  (`ConfigOut.model_validate(cfg, from_attributes=True)`).
- **Session.** Replace `from sqlmodel import Session, SQLModel,
  create_engine` with `from sqlalchemy.orm import Session,
  sessionmaker`. `get_session()` becomes a context-manager yielding a
  `Session`.
- **Migrations.** Add `alembic` as a dependency. Initialise
  `alembic/` with a generated `env.py` that imports the declarative
  metadata, set `script_location` and `sqlalchemy.url` from
  `app.config.settings`. Generate an initial migration that creates
  the current schema; this is the new baseline.
- **`init_db()`** stops calling `create_all`. Instead, the `dev` /
  `setup` mise tasks run `alembic upgrade head`. Adapt
  `app/main.py:lifespan` and `tests/conftest.py` accordingly.
- **CLI.** Add `trip-planner db upgrade` (wraps `alembic upgrade
  head`) and `trip-planner db revision -m "..."` for ergonomics; both
  are thin shims over alembic for users who don't want to learn it.
- **Tests.** A single `tests/conftest.py` fixture creates an
  in-memory SQLite DB and runs `alembic upgrade head` once per test
  session. All existing tests keep their behaviour.

This change is intentionally a **rebuild on the same table layout**:
column names, types, and JSON-serialised columns stay identical, so
the existing `trip_planner.db` can be picked up by the new code with
a one-time alembic stamp.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `search-config`: persistence layer requirement is tightened — schema
  changes SHALL go through Alembic migrations rather than runtime
  `create_all`. The data model stays the same; the *mechanism* of
  evolving it changes.

## Impact

- **Affected code (almost everything DB-shaped):**
  - `app/models.py` — full rewrite from SQLModel to SQLAlchemy 2.0
    declarative.
  - `app/db.py` — session machinery without SQLModel.
  - `app/schemas.py` — add explicit ORM → Pydantic adapters and the
    missing `*In` mirrors.
  - `app/main.py` — drop `init_db()` from lifespan; assume migrations
    have run.
  - `app/api/configs.py`, `app/api/runs.py`, `app/api/quota.py` —
    update imports (no SQLModel) and replace `session.exec(select(...))`
    with `session.scalars(select(...))` per SA 2.0.
  - `app/orchestrator/runner.py` — same session/select migration.
  - `app/cli.py` — drop `init_db()`; add `db upgrade` / `db revision`.
  - `app/seed.py` — same session migration.
- **New files/dirs:**
  - `alembic.ini`
  - `alembic/env.py`
  - `alembic/script.py.mako`
  - `alembic/versions/0001_initial.py` (auto-generated baseline)
- **`pyproject.toml`:** add `alembic>=1.13`, `sqlalchemy>=2.0`, remove
  `sqlmodel`.
- **`mise.toml`:**
  - `[tasks.install]` unchanged.
  - `[tasks.setup]`: replace `uv run trip-planner init` with
    `uv run trip-planner db upgrade`.
  - `[tasks.dev]`: same swap in the first-run guard.
  - Add `[tasks.migrate]` for `uv run alembic upgrade head` and
    `[tasks.revision]` for `uv run alembic revision --autogenerate -m`.
- **`README.md`:** update CLI table and setup steps. Mention that the
  DB layout is wire-compatible with the pre-migration `trip_planner.db`
  via `alembic stamp head`.
- **Tests:** `tests/conftest.py` (new) replaces the implicit
  `init_db()` call across tests with a session-scoped migration run.
- **Risk:** A non-trivial refactor. Worth doing in one PR with
  thorough test coverage rather than piecemeal. Dependency on
  `seed-openspec-specs` so the modified `search-config` requirement
  has a baseline to MODIFY.
