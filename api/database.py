import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/deploypilot.db"
)

settings = {}

if DATABASE_URL.startswith("sqlite"):
    settings["connect_args"] = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    **settings
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False
)

Base = declarative_base()


def ensure_user_role_schema():
    """Add the role column to older databases and preserve the configured admin."""
    inspector = inspect(engine)

    if "users" not in inspector.get_table_names():
        return

    column_names = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    with engine.begin() as connection:
        if "role" not in column_names:
            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'USER'"
                )
            )

        admin_email = os.getenv(
            "ADMIN_EMAIL",
            "admin@deploypilot.ai"
        ).strip().lower()

        connection.execute(
            text(
                "UPDATE users "
                "SET role = 'ADMIN' "
                "WHERE lower(email) = :admin_email"
            ),
            {"admin_email": admin_email}
        )


def get_db():
    database = SessionLocal()

    try:
        yield database
    finally:
        database.close()
