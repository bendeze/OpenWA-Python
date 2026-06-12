import pytest
import json

def test_create_session(client, db_session):
    response = client.post(
        "/api/sessions",
        headers={"X-API-Key": "secret-key"},
        json={"name": "test-session-1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "test-session-1"
    assert data["status"] == "created"

def test_get_sessions(client, db_session):
    # Create first
    client.post(
        "/api/sessions",
        headers={"X-API-Key": "secret-key"},
        json={"name": "test-session-2"}
    )
    
    response = client.get("/api/sessions", headers={"X-API-Key": "secret-key"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(s["name"] == "test-session-2" for s in data)

def test_start_session(client, db_session, mocker):
    # Mock redis publish
    mock_publish = mocker.patch("redis_client.redis_client.publish", new_callable=mocker.AsyncMock)
    
    # Create a session
    create_res = client.post(
        "/api/sessions",
        headers={"X-API-Key": "secret-key"},
        json={"name": "test-session-3"}
    )
    session_id = create_res.json()["id"]

    # Start session
    response = client.post(
        f"/api/sessions/{session_id}/start",
        headers={"X-API-Key": "secret-key"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Starting session..."
    
    # Verify redis publish was called with correct channel and action
    mock_publish.assert_called_once()
    args, _ = mock_publish.call_args
    assert args[0] == "wa_commands"
    payload = json.loads(args[1])
    assert payload["action"] == "START_SESSION"
    assert payload["session_id"] == int(session_id)

def test_stop_session(client, db_session, mocker):
    mock_publish = mocker.patch("redis_client.redis_client.publish", new_callable=mocker.AsyncMock)
    
    create_res = client.post(
        "/api/sessions",
        headers={"X-API-Key": "secret-key"},
        json={"name": "test-session-4"}
    )
    session_id = create_res.json()["id"]

    response = client.post(
        f"/api/sessions/{session_id}/stop",
        headers={"X-API-Key": "secret-key"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Session stopped"
    
    # Verify redis publish was called
    mock_publish.assert_called_once()
    payload = json.loads(mock_publish.call_args[0][1])
    assert payload["action"] == "LOGOUT"

def test_delete_session(client, db_session):
    create_res = client.post(
        "/api/sessions",
        headers={"X-API-Key": "secret-key"},
        json={"name": "test-session-delete"}
    )
    session_id = create_res.json()["id"]

    response = client.delete(
        f"/api/sessions/{session_id}",
        headers={"X-API-Key": "secret-key"}
    )
    assert response.status_code == 200

    # Verify it's gone
    get_res = client.get("/api/sessions", headers={"X-API-Key": "secret-key"})
    data = get_res.json()
    assert not any(str(s["id"]) == str(session_id) for s in data)

def test_get_session_stats(client, db_session):
    response = client.get("/api/sessions/stats/overview", headers={"X-API-Key": "secret-key"})
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "ready" in data
    assert "active" in data
