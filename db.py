from fastapi import Request
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./todo.db"

db_engine: Engine | None = None

Base = declarative_base()

def connect_to_db() -> Engine:
    global db_engine
    if not db_engine:
        db_engine = create_engine(
            url=DATABASE_URL
        )
    return db_engine


def get_db_session():
    session_local = sessionmaker(
        bind=db_engine,
        autocommit=False,
        autoflush=False
    )
    db = session_local()
    return db


def get_db_session_for_request(
    request: Request
):
    return request.state.db_session
