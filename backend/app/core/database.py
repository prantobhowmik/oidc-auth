from sqlalchemy import URL, create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# python-oracledb in thin mode (no Oracle Client install needed).
# URL.create handles special characters in the password safely.
DATABASE_URL = URL.create(
    "oracle+oracledb",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    query={"service_name": settings.DB_SERVICE_NAME},
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


@event.listens_for(engine, "connect")
def _set_utc_session_timezone(dbapi_connection, _record):
    # Oracle's session time zone follows the host (e.g. +06:00), and the driver
    # returns timestamps without tz info. Pin every connection to UTC so
    # server defaults (CURRENT_TIMESTAMP) and Python UTC values agree.
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("ALTER SESSION SET TIME_ZONE = '+00:00'")
    finally:
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
