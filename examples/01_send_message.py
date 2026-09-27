"""
Basic Example: Sending a message using OpenWA Python SDK.
"""

from openwa import OpenWAClient

# 1. Initialize client pointing to your running OpenWA instance
client = OpenWAClient(base_url="http://localhost:3000", api_key="your_api_key_here")

# 2. List active WhatsApp sessions
sessions = client.sessions.list()
print(f"Active sessions: {sessions}")

# 3. Send a message
# client.messages.send_text(
#     session_id="default",
#     data={
#         "chatId": "1234567890@c.us",
#         "text": "Hello from OpenWA Python!"
#     }
# )
