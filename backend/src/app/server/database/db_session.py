from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from core.utils.file_util import get_data_path
from src.app.utils.logger_util import log_info, log_error, log_debug
from src.app.server.database.orm_models import Base

_path = get_data_path()/"database"/"app.db"
log_debug(_path)
DB_PATH = Path(_path)

# DuckDB only allows a single OS-level connection to a database file at a time,
# even from within the same process. StaticPool keeps exactly one underlying
# DBAPI connection alive for the lifetime of the engine and hands it out to
# every Session, instead of opening a new connection per session, or callers
# would collide with "file is being used by another process" and silently
# lose writes.
engine = create_engine(
    f"duckdb:///{DB_PATH}",
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# FastAPI runs sync route handlers in a threadpool, so concurrent requests can
# each get a Session bound to the same shared StaticPool connection at once.
# Without serializing access, two threads racing to begin a transaction on
# that single physical connection raise "cannot start a transaction within a
# transaction". This lock enforces one active session at a time.
_db_lock = Lock()


@contextmanager
def get_db_session() -> Iterator[Session]:
    """
    Context manager yielding a SQLAlchemy session backed by the shared
    single DuckDB connection. Commits on success, rolls back and re-raises
    on failure, and always closes the session.
    """
    with _db_lock:
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def initialize_database():
    """
    Initialize DuckDB database with required tables on startup via the
    SQLAlchemy ORM metadata (see orm_models.py for table/column definitions).
    Creates: users, chat_sessions, chat_messages, model_providers.
    """
    try:
        # Ensure the database directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        Base.metadata.create_all(engine)

        log_info(f"Database initialized successfully at {DB_PATH}")

    except Exception as e:
        log_error(f"Failed to initialize database: {e}")
        raise


# if __name__ == "__main__":
#     initialize_database()
