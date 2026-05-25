## 1. Dependencies

- [x] 1.1 In `pyproject.toml`, replace `sqlmodel>=0.0.22` with
      `sqlalchemy>=2.0` and add `alembic>=1.13`.
- [x] 1.2 Run `uv lock` (or let `mise run install` re-resolve).

## 2. ORM rewrite (`app/models.py`)

- [x] 2.1 Define `class Base(DeclarativeBase): pass`.
- [x] 2.2 Port `Config`, `Leg`, `Run`, `Fare`, `Itinerary` to SA 2.0
      typed-declarative (`Mapped[...]`, `mapped_column(...)`),
      preserving every column name, type, nullability, default,
      and JSON storage decision from the current SQLModel classes.
- [x] 2.3 Move `utcnow()` helper to the top of the file; keep the
      same `datetime.now(timezone.utc)` semantics.
- [x] 2.4 Keep `Leg.is_round_trip` as a Python `@property`.

## 3. Session machinery (`app/db.py`)

- [x] 3.1 Replace `from sqlmodel import ...` with
      `from sqlalchemy.orm import Session, sessionmaker` and
      `from sqlalchemy import create_engine`.
- [x] 3.2 Build a `SessionLocal = sessionmaker(bind=engine,
      expire_on_commit=False)`.
- [x] 3.3 Rewrite `get_session()` as a context manager yielding a
      `Session`; remove `init_db()` entirely.
- [x] 3.4 Keep `connect_args={"check_same_thread": False}` for the
      SQLite case.

## 4. Pydantic IO schemas (`app/schemas.py`)

- [x] 4.1 Audit current schemas: every ORM column must have a
      corresponding Pydantic representation in the appropriate IO
      model. Add missing fields (e.g. round-trip ones on `LegPayload`
      are already there — keep them).
- [x] 4.2 Add `model_config = {"from_attributes": True}` to every
      `*Out` schema so `Out.model_validate(orm_row)` works.
- [x] 4.3 Replace ad-hoc dict construction in `api/configs.py:_to_out`
      with `ConfigOut.model_validate(cfg)` plus a list comprehension
      for legs.

## 5. API + orchestrator + CLI session migration

- [x] 5.1 In `app/api/configs.py`, `app/api/runs.py`,
      `app/api/quota.py`: replace `session.exec(select(...)).all()`
      with `session.scalars(select(...)).all()`; replace
      `session.exec(select(...)).first()` with
      `session.scalars(select(...)).first()`.
- [x] 5.2 In `app/orchestrator/runner.py`: same `exec` →
      `scalars` migration; remove `from sqlmodel import Session,
      select` and use `sqlalchemy` imports.
- [x] 5.3 In `app/seed.py`: same migration; remove `init_db()` call
      (callers run `alembic upgrade head` instead).
- [x] 5.4 In `app/cli.py`: drop `init_db()` from each command body;
      add `db` typer subgroup with `upgrade` and `revision`
      commands.
- [x] 5.5 In `app/main.py:lifespan`: remove `init_db()` call; add a
      startup check that the `alembic_version` table exists, raising
      a clear `RuntimeError("Run `mise run migrate` (or `alembic
      upgrade head`) before starting the server.")` if not.

## 6. Alembic setup

- [x] 6.1 Run `uv run alembic init alembic` to scaffold
      `alembic.ini` + `alembic/`.
- [x] 6.2 In `alembic/env.py`, set `target_metadata = Base.metadata`
      (imported from `app.models`).
- [x] 6.3 In `alembic/env.py`, read `sqlalchemy.url` from
      `app.config.settings.database_url`.
- [x] 6.4 In `alembic.ini`, point `script_location = alembic` and
      leave `sqlalchemy.url` blank (env.py overrides).
- [x] 6.5 Generate the baseline: `uv run alembic revision
      --autogenerate -m "initial schema"`; review the output.
- [x] 6.6 Diff the generated migration's emitted DDL against the
      current schema (`sqlite3 trip_planner.db.bak .schema`); hand-edit
      the migration to match exactly. Rename to
      `alembic/versions/0001_initial.py` for readability.

## 7. CLI shims

- [x] 7.1 Add `trip-planner db upgrade [revision="head"]` that calls
      `alembic.config.main(["upgrade", revision])`.
- [x] 7.2 Add `trip-planner db revision -m <message>
      [--autogenerate]` that calls
      `alembic.config.main(["revision", "-m", message, ...])`.
- [x] 7.3 Drop `trip-planner init` (or alias it to `db upgrade`
      for backwards compatibility; pick one and document in README).

## 8. mise tasks

- [x] 8.1 In `mise.toml [tasks.setup]`, replace `uv run trip-planner
      init` with `uv run trip-planner db upgrade`.
- [x] 8.2 In `mise.toml [tasks.dev]`, replace the
      `uv run trip-planner init` line in the first-run guard with
      `uv run trip-planner db upgrade`.
- [x] 8.3 Add `[tasks.migrate]` that runs `uv run alembic upgrade
      head`.
- [x] 8.4 Add `[tasks.revision]` that runs `uv run alembic revision
      --autogenerate -m`. Document that the message follows
      `mise run revision -- "add foo column"`.
- [x] 8.5 Update the README task table accordingly.

## 9. Tests

- [x] 9.1 Add `tests/conftest.py` with a session-scoped fixture that
      sets `DATABASE_URL=sqlite:///:memory:`, runs `alembic upgrade
      head`, and yields a `Session` factory.
- [x] 9.2 Update each existing test that imported `init_db` to use
      the new fixture.
- [x] 9.3 Add a migration test: `tests/test_migrations.py` that
      runs `alembic upgrade head` then `alembic downgrade base`
      against a temporary SQLite file, asserting both succeed.
- [x] 9.4 Run `mise run test` — all tests pass.

## 10. README

- [x] 10.1 Update `## Setup` to mention `mise run migrate` (or that
      `mise run setup` runs it implicitly).
- [x] 10.2 Update the CLI table: remove `trip-planner init`; add
      `trip-planner db upgrade` and `trip-planner db revision`.
- [x] 10.3 Update the mise-tasks table to include `migrate` and
      `revision`.
- [x] 10.4 Add a "DB migrations" sub-section noting that the schema
      is wire-compatible with pre-migration DBs via `alembic stamp
      head`.

## 11. Spec + validate

- [x] 11.1 Update `openspec/specs/search-config/spec.md` per this
      change's delta in `specs/`.
- [x] 11.2 Run `openspec validate port-models-to-pydantic-with-alembic
      --strict`.
- [x] 11.3 Smoke test against a copy of an existing
      `trip_planner.db`: run `alembic stamp head`, then
      `mise run quota` and `mise run run -- <id>`; expect identical
      output to the SQLModel version.
