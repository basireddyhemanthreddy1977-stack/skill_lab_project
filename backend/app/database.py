from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


_database_url = make_url(settings.database_url)
_is_sqlite = _database_url.get_backend_name() == "sqlite"

# SQLite creates a database file, but not missing parent folders. Explicit relative
# URLs in backend/.env therefore need their directory created before create_all().
if _is_sqlite and _database_url.database not in (None, "", ":memory:"):
    _sqlite_path = Path(_database_url.database).expanduser()
    if not _sqlite_path.is_absolute():
        _sqlite_path = Path.cwd() / _sqlite_path
    try:
        _sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise RuntimeError(f"Cannot create SQLite database folder '{_sqlite_path.parent}': {exc}") from exc
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False, "timeout": 30} if _is_sqlite else {},
)


@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_connection, _record):
    if not _is_sqlite:
        return
    cur = dbapi_connection.cursor()
    cur.execute("PRAGMA foreign_keys=ON")  # SQLite ignores FKs unless enabled per connection
    cur.execute("PRAGMA journal_mode=WAL")
    cur.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # an uncommitted transaction is rolled back on close
