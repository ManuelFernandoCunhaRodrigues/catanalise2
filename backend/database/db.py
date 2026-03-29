import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_URL = f"sqlite:///{(BASE_DIR / 'database.db').as_posix()}"
ANALYSIS_TABLE = "analyses"

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)


def get_engine() -> Engine:
    global _engine

    if _engine is None:
        database_url = get_database_url()
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        _engine = create_engine(database_url, future=True, pool_pre_ping=True, connect_args=connect_args)

    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory

    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)

    return _session_factory


@contextmanager
def session_context() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    _ensure_column(engine, ANALYSIS_TABLE, "analysis_payload", "TEXT")


def _ensure_column(engine: Engine, table_name: str, column_name: str, column_definition: str) -> None:
    existing_columns = {column["name"] for column in inspect(engine).get_columns(table_name)}
    if column_name in existing_columns:
        return

    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"))
