import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


DB_PATH = Path(__file__).resolve().parent.parent / "database.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def connection_context() -> Iterator[sqlite3.Connection]:
    """
    Garante commit, rollback e fechamento real da conexao.
    """
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    """
    Cria o banco e a tabela automaticamente na primeira execucao.
    """
    with connection_context() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                score INTEGER NOT NULL,
                nivel TEXT NOT NULL,
                erros TEXT NOT NULL,
                alertas TEXT NOT NULL,
                inconsistencias TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
