"""Test health endpoints."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from fastapi.testclient import TestClient
from fpl_toolkit.service.api import app

client = TestClient(app)


def test_root_ok():
    """Test root endpoint returns 200 with correct format."""
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "fpl-toolkit"


def test_head_root_ok():
    """Test HEAD root endpoint returns 200."""
    r = client.head("/")
    assert r.status_code == 200


def test_healthz_ok():
    """Test healthz endpoint returns 200 with correct format."""
    r = client.get("/healthz")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True


def test_health_still_works():
    """Test original health endpoint still works."""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "fpl-toolkit-api"


if __name__ == "__main__":
    # Run basic tests manually
    print("Testing root endpoint...")
    test_root_ok()
    print("✅ Root endpoint test passed")
    
    print("Testing HEAD root endpoint...")
    test_head_root_ok()
    print("✅ HEAD root endpoint test passed")
    
    print("Testing healthz endpoint...")
    test_healthz_ok()
    print("✅ Healthz endpoint test passed")
    
    print("Testing original health endpoint...")
    test_health_still_works()
    print("✅ Health endpoint test passed")
    
    print("All tests passed!")