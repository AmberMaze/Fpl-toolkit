"""Test database engine and initialization."""
import os
import tempfile
import pytest
from sqlalchemy import text
from src.fpl_toolkit.db.engine import get_engine, get_session, init_db, close_db, get_database_url


class TestDatabaseEngine:
    """Test database engine functionality."""
    
    def setup_method(self):
        """Setup test method with clean state."""
        close_db()  # Ensure clean state
    
    def teardown_method(self):
        """Cleanup after test method."""
        close_db()
    
    def test_get_database_url_default(self, monkeypatch):
        """Test default SQLite database URL."""
        monkeypatch.delenv("DATABASE_URL", raising=False)
        url = get_database_url()
        assert url.startswith("sqlite:///")
        assert url.endswith("fpl_toolkit.db")
    
    def test_get_database_url_from_env(self, monkeypatch):
        """Test database URL from environment variable."""
        test_url = "postgresql://user:pass@localhost/test"
        monkeypatch.setenv("DATABASE_URL", test_url)
        url = get_database_url()
        assert url == test_url
    
    def test_get_engine_sqlite(self, monkeypatch):
        """Test SQLite engine creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
            
            engine = get_engine()
            assert engine is not None
            assert str(engine.url).startswith("sqlite:///")
    
    def test_get_session(self, monkeypatch):
        """Test session creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
            
            session = get_session()
            assert session is not None
            
            # Test basic query
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            
            session.close()
    
    def test_init_db(self, monkeypatch):
        """Test database initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
            
            # Initialize database
            init_db()
            
            # Verify tables exist
            engine = get_engine()
            inspector = engine.dialect.get_table_names(engine.connect())
            
            expected_tables = ["players", "gameweek_history", "projections", "decision_scenarios"]
            for table in expected_tables:
                assert table in inspector
    
    def test_close_db(self, monkeypatch):
        """Test database connection cleanup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
            
            # Create engine and session
            engine = get_engine()
            session = get_session()
            
            assert engine is not None
            assert session is not None
            
            session.close()
            
            # Close database
            close_db()
            
            # Verify cleanup
            from src.fpl_toolkit.db.engine import engine as global_engine
            from src.fpl_toolkit.db.engine import SessionLocal
            
            assert global_engine is None
            assert SessionLocal is None