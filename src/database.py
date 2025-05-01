"""This module is responsible for creating database and tables."""

from sqlmodel import SQLModel, create_engine, text

SQLITE_FILE_NAME = "./data/database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL)


def create_db_and_tables():
    """Creates database and tables."""
    SQLModel.metadata.create_all(engine)
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))
