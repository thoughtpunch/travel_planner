"""Migration round-trip test: upgrade head, then downgrade base."""

from __future__ import annotations

from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect


def _alembic_config(db_url: str) -> AlembicConfig:
    cfg = AlembicConfig("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


def test_alembic_upgrade_then_downgrade(tmp_path):
    db_path = tmp_path / "migrate.db"
    db_url = f"sqlite:///{db_path}"
    cfg = _alembic_config(db_url)

    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    tables = set(inspect(engine).get_table_names())
    expected = {"alembic_version", "config", "leg", "run", "fare", "itinerary"}
    assert expected.issubset(tables), f"missing tables: {expected - tables}"

    command.downgrade(cfg, "base")
    tables = set(inspect(engine).get_table_names())
    # alembic_version remains; all app tables are gone.
    assert tables.intersection({"config", "leg", "run", "fare", "itinerary"}) == set()
