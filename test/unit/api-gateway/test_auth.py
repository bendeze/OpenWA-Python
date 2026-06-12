import pytest
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../api-gateway")))

import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_validate_api_key_no_key(client):
    """Test accessing auth endpoint without an API key."""
    response = client.post("/api/auth/validate")
    assert response.status_code == 422

def test_validate_api_key_invalid(client):
    """Test accessing auth endpoint with an invalid API key."""
    response = client.post("/api/auth/validate", headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API Key"

def test_validate_api_key_valid_secret(client):
    """Test accessing auth endpoint with the master secret-key."""
    response = client.post("/api/auth/validate", headers={"X-API-Key": "secret-key"})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["role"] == "admin"

def test_validate_api_key_from_db(client, db_session):
    """Test accessing auth endpoint with a valid API key from the database."""
    # Insert a valid API key into the test database
    new_key = models.ApiKey(
        name="Test Key",
        key="test-db-api-key",
        role="operator",
        is_active=True,
    )
    db_session.add(new_key)
    db_session.commit()

    # Test the validation
    response = client.post("/api/auth/validate", headers={"X-API-Key": "test-db-api-key"})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["role"] == "operator"

def test_get_api_keys(client, db_session):
    """Test retrieving the list of API keys."""
    # Need to provide valid auth to retrieve keys
    # Let's insert a key first
    new_key = models.ApiKey(
        name="Test Key 1",
        key="test-key-1",
        role="admin",
        is_active=True,
    )
    db_session.add(new_key)
    db_session.commit()

    response = client.get("/api/auth/api-keys", headers={"X-API-Key": "secret-key"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Key 1"
    assert data[0]["role"] == "admin"
    assert "test-key-1" in data[0]["fullKey"]
