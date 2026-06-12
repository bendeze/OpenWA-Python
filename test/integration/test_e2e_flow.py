import pytest
import json

def test_full_session_lifecycle(client, db_session, mocker):
    """
    End-to-End integration test covering:
    1. Creating a session
    2. Getting the session list
    3. Starting the session
    4. Stopping the session
    5. Deleting the session
    """
    mock_publish = mocker.patch("redis_client.redis_client.publish", new_callable=mocker.AsyncMock)
    
    # 1. Create
    res = client.post(
        "/api/sessions",
        headers={"X-API-Key": "secret-key"},
        json={"name": "e2e-session"}
    )
    assert res.status_code == 200
    session_id = res.json()["id"]

    # 2. Get List
    res = client.get("/api/sessions", headers={"X-API-Key": "secret-key"})
    assert any(s["id"] == session_id for s in res.json())

    # 3. Start
    res = client.post(
        f"/api/sessions/{session_id}/start",
        headers={"X-API-Key": "secret-key"}
    )
    assert res.status_code == 200
    
    # Verify redis publish
    mock_publish.assert_called_with("wa_commands", mocker.ANY)

    # 4. Stop
    res = client.post(
        f"/api/sessions/{session_id}/stop",
        headers={"X-API-Key": "secret-key"}
    )
    assert res.status_code == 200

    # 5. Delete
    res = client.delete(
        f"/api/sessions/{session_id}",
        headers={"X-API-Key": "secret-key"}
    )
    assert res.status_code == 200

    # Verify deleted
    res = client.get("/api/sessions", headers={"X-API-Key": "secret-key"})
    assert not any(str(s["id"]) == str(session_id) for s in res.json())

def test_full_messaging_flow(client, db_session, mocker):
    """
    End-to-End messaging integration:
    1. Send a text message (mocks worker response)
    2. Retrieve message logs
    """
    mock_rpc = mocker.patch("routers.messages.rpc_call", new_callable=mocker.AsyncMock)
    mock_rpc.return_value = {"messageId": "e2e_msg", "timestamp": 123456}

    # 1. Send Text
    res = client.post(
        "/api/sessions/1/messages/send-text",
        headers={"X-API-Key": "secret-key"},
        json={"chatId": "123@c.us", "text": "e2e test message"}
    )
    assert res.status_code == 200
    assert res.json()["messageId"] == "e2e_msg"
