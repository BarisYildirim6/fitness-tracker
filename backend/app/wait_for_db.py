from __future__ import annotations

import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from app.core.config import settings


def wait_for_database(timeout_seconds: int = 60, interval_seconds: int = 2) -> None:
    deadline = time.monotonic() + timeout_seconds
    engine = create_engine(settings.database_url, pool_pre_ping=True)

    while True:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except OperationalError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(interval_seconds)
        finally:
            engine.dispose()


def main() -> None:
    wait_for_database()
    print("Database is ready.")


if __name__ == "__main__":
    main()
