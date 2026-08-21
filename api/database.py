import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
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


def get_db():
    database = SessionLocal()

    try:
        yield database
    finally:
        database.close()