#!/usr/bin/env python3
"""
Basic tests for Lumber Estimator API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.api.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_docs_endpoint():
    """Test that docs endpoint is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_redoc_endpoint():
    """Test that redoc endpoint is accessible"""
    response = client.get("/redoc")
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__]) 