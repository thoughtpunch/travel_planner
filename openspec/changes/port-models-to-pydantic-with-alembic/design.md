## Context

`app/models.py` uses SQLModel — one class per table that doubles as a
Pydantic schema. `app/schemas.py` already maintains parallel pure
Pydantic IO models. The two have started to drift (Leg round-trip
fields landed on the table before the schema). The DB has no
migration history — `init_db()` calls `SQLModel.metadata.create_all`
each boot, which is fine for the throwaway dev DB but a footgun the
moment a real deployment retains the file across versions.

## Goals / Non-Goals

**Goals:**

- Single discipline: Pydantic for IO (`app/schemas.py`), SQLAlchemy
  2.0 declarative for persistence (`app/models.py`).
- Real migrations via Alembic, baseline = current schema.
- Wire-compatible DB layout — same table names, same columns. Existing
  `trip_planner.db` files can be carried forward with one
  `alembic stamp head`.
- No behaviour change in API responses or DB contents.

**Non-Goals:**

- Switching to async SQLAlchemy. (Possible follow-up; orthogonal.)
- Renaming tables or columns. (Would force a real data migration; not
  worth the blast radius in this change.)
- Adding row-level migration logic / DDL beyond the baseline. (Future
  schema additions will write their own revisions.)
- Replacing SQLite. (Engine stays; URL still
  `sqlite:///./trip_planner.db`.)
- Splitting Pydantic IO models per-endpoint. The existing
  `ConfigPayload` / `ConfigOut` shape is fine.

## Decisions

### Decision 1: SQLAlchemy 2.0 typed-style declarative

Use `from sqlalchemy.orm import DeclarativeBase, Mapped,
mapped_column` syntax. It's the idiomatic 2.0 form, ships with
mypy/pyright support, and reads naturally next to Pydantic v2.
Avoids the legacy `Column(...)` style mixed with `__tablename__`
strings.

```python
class Base(DeclarativeBase):
    pass

class Config(Base):
    __tablename__ = "config"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    budget_party_total: Mapped[int]
    passengers: Mapped[dict[str, int]] = mapped_column(JSON)
    # ...
```

### Decision 2: JSON columns stay JSON

Every list/dict field today is stored via SQLAlchemy `JSON`. We keep
that. Alembic's autogenerate handles `JSON` correctly on SQLite (it
emits `JSON` which sqlite stores as TEXT) — same on-disk shape as
SQLModel produced.

### Decision 3: Alembic baseline = current schema

Run autogenerate against an empty DB after the model rewrite; the
resulting `0001_initial.py` should diff cleanly against the existing
schema. Verification step: drop a copy of the current
`trip_planner.db`, run `alembic stamp head`, run a `mise run run`,
confirm identical results. If autogenerate produces drift, hand-edit
the migration to match the existing file before tagging it as the
baseline.

### Decision 4: `init_db()` → `alembic upgrade head`

`init_db()` is removed. Its callers (`app/main.py:lifespan`,
`app/cli.py:init/seed/configs/quota/run`) either drop the call
entirely or invoke the new `db upgrade` CLI command. The dev-server
first-run guard in `mise.toml [tasks.dev]` checks for the DB file and
runs `db upgrade` + `seed` once.

### Decision 5: CLI shims, not full passthrough

`trip-planner db upgrade` and `trip-planner db revision -m "..."` are
small typer subcommands that call `alembic.config.main([...])`
in-process. This means `mise run migrate` works without users
needing `alembic` on `$PATH`, but power users can still `uv run
alembic upgrade head` directly.

### Decision 6: Tests use a session-scoped in-memory DB

`tests/conftest.py` (new) sets a per-session sqlite-in-memory URL,
runs `alembic upgrade head` once, and yields a session factory.
Existing tests that called `init_db()` get the fixture instead. This
keeps tests fast (no file I/O) and exercises the migration on every
CI run.

### Decision 7: Capability spec delta — search-config only

The other capability specs (fare-search, fare-validation,
itinerary-orchestration, web-api, web-ui) don't say anything about
*how* persistence works — they describe behaviour. Only
`search-config` makes a claim about persistence ("persist in SQLite")
and that's where we tighten the requirement to specify Alembic. The
other specs ride along unchanged.

## Risks / Trade-offs

- **Risk:** Autogenerate produces a baseline that diffs subtly from
  the SQLModel-emitted schema (e.g. column nullability flag, default
  expression). **Mitigation:** dump the schema before and after with
  `sqlite3 trip_planner.db .schema`, diff, hand-edit the baseline if
  needed.
- **Risk:** Tests break because they relied on SQLModel's Pydantic
  validation at the DB layer (rare, but possible for `passengers:
  dict[str, int]` typing). **Mitigation:** keep IO validation in
  `schemas.py`; ORM models trust the schema layer above them.
- **Trade-off:** Two model files (`models.py` for ORM, `schemas.py`
  for IO) instead of one SQLModel file. More boilerplate, clearer
  separation. Worth it for the migration discipline alone.
- **Trade-off:** Alembic adds one dependency and a few config files.
  Standard cost for any production-shaped Python project; we accept
  it.
- **Risk:** Someone runs the new code against an old `trip_planner.db`
  without stamping. **Mitigation:** add a startup check in
  `app.main.lifespan` that queries `alembic_version`; if the table is
  missing, raise a clear error telling the operator to run
  `mise run migrate` or `mise run setup` (which the README also
  states).
