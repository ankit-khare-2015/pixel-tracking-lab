import logging
import time

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db() -> None:
    """Retry a simple query so backend can start while Postgres is booting."""
    retries = settings.db_connect_retries
    delay = settings.db_retry_sleep_seconds

    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Connected to database")
            return
        except Exception as exc:
            logger.warning("Database not ready (attempt %s/%s): %s", attempt, retries, exc)
            time.sleep(delay)

    raise RuntimeError("Database connection failed after retries")
