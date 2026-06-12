import pytest
from models import MessageLog
import datetime

def test_get_messages(client, db_session):
    # Insert some dummy logs
    log1 = MessageLog(
        session_id=1,
        msg_id="msg_1",
        from_me=True,
        from_str="me",
        to_str="them",
        body="hello",
        type="chat",
        timestamp=int(datetime.datetime.utcnow().timestamp())
    )
    db_session.add(log1)
    db_session.commit()

    response = client.get("/api/sessions/1/messages", headers={"X-API-Key": "secret-key"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["body"] == "hello"

def test_send_message_success(client, db_session, mocker):
    mock_rpc = mocker.patch("routers.messages.rpc_call", new_callable=mocker.AsyncMock)
    mock_rpc.return_value = {"messageId": "new_msg_id", "timestamp": 12345678}

    response = client.post(
        "/api/sessions/1/messages/send-text",
        headers={"X-API-Key": "secret-key"},
        json={"chatId": "123456@c.us", "text": "hello test"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["messageId"] == "new_msg_id"
    mock_rpc.assert_called_once_with(
        "SEND_TEXT", 
        {"session_id": "1", "to": "123456@c.us", "text": "hello test"}, 
        timeout=60.0
    )

def test_send_message_timeout(client, db_session, mocker):
    mock_rpc = mocker.patch("routers.messages.rpc_call", new_callable=mocker.AsyncMock)
    mock_rpc.side_effect = TimeoutError()

    response = client.post(
        "/api/sessions/1/messages/send-text",
        headers={"X-API-Key": "secret-key"},
        json={"chatId": "123456@c.us", "text": "hello test"}
    )
    
    # Custom exception handler in router returns 400 on timeout
    assert response.status_code == 400
    assert "timed out" in response.json()["message"]
