import pytest
import sys
import os

# Add root directory to path so 'sdk' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from sdk.python.openwa import OpenWAClient, AsyncOpenWAClient, OpenWAAPIError

@pytest.fixture
def sync_client():
    return OpenWAClient(base_url="http://localhost:2785", api_key="test-key")

@pytest.fixture
def async_client():
    return AsyncOpenWAClient(base_url="http://localhost:2785", api_key="test-key")

def test_sync_get_sessions(sync_client, mocker):
    mock_request = mocker.patch("httpx.Client.request")
    
    # Mock Response
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "name": "test-session"}]
    mock_request.return_value = mock_response

    sessions = sync_client.sessions.list()
    assert len(sessions) == 1
    assert sessions[0]["name"] == "test-session"
    mock_request.assert_called_once_with(
        "GET", 
        "http://localhost:2785/api/sessions",
        headers={"Content-Type": "application/json", "X-API-Key": "test-key"}
    )

def test_sync_api_error(sync_client, mocker):
    mock_request = mocker.patch("httpx.Client.request")
    
    # Mock error Response
    mock_response = mocker.Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"detail": "Invalid API Key"}
    mock_request.return_value = mock_response

    with pytest.raises(OpenWAAPIError) as exc_info:
        sync_client.sessions.list()
    
    assert exc_info.value.status_code == 401
    assert "Invalid API Key" in exc_info.value.message

@pytest.mark.asyncio
async def test_async_create_session(async_client, mocker):
    mock_request = mocker.patch("httpx.AsyncClient.request")
    
    # Mock async response
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "123", "name": "async-session"}
    mock_request.return_value = mock_response

    session = await async_client.sessions.create("async-session")
    assert session["id"] == "123"
    assert session["name"] == "async-session"
    mock_request.assert_called_once_with(
        "POST",
        "http://localhost:2785/api/sessions",
        headers={"Content-Type": "application/json", "X-API-Key": "test-key"},
        json={"name": "async-session"}
    )
