"""Test fixtures.

Each test that needs DB access uses an isolated on-disk SQLite file (so the
runner's separate Session can read what the test wrote) and runs Alembic up
to head once via `_engine_with_migrations`.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def db_engine(tmp_path, monkeypatch):
    """Per-test sqlite DB pointed at a tmp file, migrated to head."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    from importlib import reload

    import app.config as config_module
    reload(config_module)
    import app.db as db_module
    reload(db_module)

    # Apply migrations to head against the per-test DB URL. Use the Alembic
    # Python API rather than the CLI so this stays in-process.
    from alembic import command
    from alembic.config import Config as AlembicConfig

    cfg = AlembicConfig("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", config_module.settings.database_url)
    command.upgrade(cfg, "head")

    return db_module.engine
