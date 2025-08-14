"""Database engine and session management."""
import os
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool

# Declarative base for all models
Base = declarative_base()

# Global session maker
SessionLocal: Optional[sessionmaker] = None
engine: Optional[Engine] = None


def get_database_url() -> str:
    """Get database URL from environment or fallback to SQLite."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Fallback to SQLite
    db_path = os.path.join(os.getcwd(), "fpl_toolkit.db")
    return f"sqlite:///{db_path}"


def get_engine() -> Engine:
    """Get or create database engine."""
    global engine
    if engine is None:
        database_url = get_database_url()
        
        if database_url.startswith("sqlite"):
            # SQLite specific configuration
            engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            # PostgreSQL and other databases
            engine = create_engine(database_url, echo=False)
    
    return engine


def get_session() -> Session:
    """Get database session."""
    global SessionLocal
    if SessionLocal is None:
        engine = get_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal()


def init_db() -> None:
    """Initialize database tables."""
    from . import models  # Import models to register them
    
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def close_db() -> None:
    """Close database connections."""
    global engine, SessionLocal
    if engine:
        engine.dispose()
        engine = None
    SessionLocal = None