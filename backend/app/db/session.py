from __future__ import annotations
import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import get_settings
from app.db.models import Base

def _database_url() -> str:
    url = os.getenv("DATABASE_URL") or get_settings().database_url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

DATABASE_URL = _database_url()
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def init_db(drop_existing: bool = False) -> None:
    if DATABASE_URL.startswith("sqlite:///"):
        Path(DATABASE_URL.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)
    if drop_existing:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def has_tables() -> bool:
    return bool(inspect(engine).get_table_names())
