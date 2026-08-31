import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, inspect, text
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


# Enable SQLite foreign key enforcement
if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(
        dbapi_connection,
        connection_record
    ):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False
)

Base = declarative_base()


def ensure_user_role_schema():
    """Add the role column to older databases and save the configured admin."""
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
                    "ADD COLUMN role VARCHAR(20) "
                    "NOT NULL DEFAULT 'USER'"
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


def ensure_prediction_history_gate_schema():
    """
    Add cold start quality gate fields to older prediction history tables.
    """
    inspector = inspect(engine)

    if "prediction_history" not in inspector.get_table_names():
        return

    column_names = {
        column["name"]
        for column in inspector.get_columns("prediction_history")
    }

    statements = {
        "gate_mode": (
            "ALTER TABLE prediction_history "
            "ADD COLUMN gate_mode VARCHAR(20)"
        ),
        "cold_start": (
            "ALTER TABLE prediction_history "
            "ADD COLUMN cold_start BOOLEAN"
        ),
        "meaningful_history_runs": (
            "ALTER TABLE prediction_history "
            "ADD COLUMN meaningful_history_runs INTEGER"
        ),
    }

    with engine.begin() as connection:
        for column_name, statement in statements.items():
            if column_name not in column_names:
                connection.execute(text(statement))


def ensure_prediction_history_user_schema():
   
    inspector = inspect(engine)

    table_names = inspector.get_table_names()

    if (
        "prediction_history" not in table_names
        or "users" not in table_names
    ):
        return

    column_names = {
        column["name"]
        for column in inspector.get_columns("prediction_history")
    }

    if "u_id" not in column_names:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE prediction_history "
                    "ADD COLUMN u_id INTEGER "
                    "REFERENCES users(id)"
                )
            )


def get_db():
    database = SessionLocal()

    try:
        yield database
    finally:
        database.close()