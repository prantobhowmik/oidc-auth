from sqlalchemy import text

from app.core.database import engine


with engine.connect() as conn:
    result = conn.execute(text("SELECT 1 FROM DUAL")).scalar()
    user = conn.execute(text("SELECT USER FROM DUAL")).scalar()
    service = conn.execute(
        text("SELECT SYS_CONTEXT('USERENV', 'SERVICE_NAME') FROM DUAL")
    ).scalar()

print(f"SELECT 1 FROM DUAL -> {result}")
print(f"Connected as {user} on service {service}")
