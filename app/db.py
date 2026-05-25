from sqlmodel import Session, SQLModel, create_engine

from .config import settings

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)


def init_db() -> None:
    from . import models  # noqa: F401 — register tables

    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
