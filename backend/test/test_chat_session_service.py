"""
Test script to verify the chat session service layer implementation.
This demonstrates the layered architecture: Routes -> Service -> Repository
"""

from backend.app.server.service.chat_session_service import ChatSessionService
from backend.app.server.schemas.chat_session_schemas import ChatSessionCreateRequest, ChatSessionUpdateRequest

def test_chat_session_service():
    """Test the chat session service functionality"""

    # Initialize service
    service = ChatSessionService()

    print("=== Testing Chat Session Service Layer ===\n")

    # Test 1: Create a chat session
    print("1. Creating a new chat session...")
    chat_session_create = ChatSessionCreateRequest(
        user_id="test_user_123",
        title="Test Chat Session"
    )

    try:
        response = service.create_chat_session(chat_session_create)
        chat_session_id = response.chat_session_id
        print(f"✓ Chat session created successfully with ID: {chat_session_id}\n")
    except Exception as e:
        print(f"✗ Failed to create chat session: {e}\n")
        return

    # Test 2: Get chat session by ID
    print(f"2. Retrieving chat session by ID: {chat_session_id}...")
    try:
        chat_session = service.get_chat_session_by_id(chat_session_id)
        if chat_session:
            print(f"✓ Chat session retrieved: {chat_session.title}\n")
        else:
            print("✗ Chat session not found\n")
    except Exception as e:
        print(f"✗ Failed to retrieve chat session: {e}\n")

    # Test 3: Get all chat sessions for user
    print(f"3. Retrieving all chat sessions for user: test_user_123...")
    try:
        response = service.get_chat_sessions_by_user("test_user_123")
        print(f"✓ Found {response.count} chat session(s) for user\n")
    except Exception as e:
        print(f"✗ Failed to retrieve chat sessions: {e}\n")

    # Test 4: Update chat session
    print(f"4. Updating chat session title...")
    chat_session_update = ChatSessionUpdateRequest(
        title="Updated Test Chat Session"
    )
    try:
        response = service.update_chat_session(chat_session_id, chat_session_update)
        if response.success:
            print(f"✓ {response.message}\n")
        else:
            print(f"✗ {response.message}\n")
    except Exception as e:
        print(f"✗ Error updating chat session: {e}\n")

    # Test 5: Archive chat session
    print(f"5. Archiving chat session...")
    try:
        response = service.archive_chat_session(chat_session_id)
        if response.success:
            print(f"✓ {response.message}\n")
        else:
            print(f"✗ {response.message}\n")
    except Exception as e:
        print(f"✗ Error archiving chat session: {e}\n")

    # Test 6: Unarchive chat session
    print(f"6. Unarchiving chat session...")
    try:
        response = service.unarchive_chat_session(chat_session_id)
        if response.success:
            print(f"✓ {response.message}\n")
        else:
            print(f"✗ {response.message}\n")
    except Exception as e:
        print(f"✗ Error unarchiving chat session: {e}\n")

    # Test 7: Delete chat session
    print(f"7. Deleting chat session...")
    try:
        response = service.delete_chat_session(chat_session_id)
        if response.success:
            print(f"✓ {response.message}\n")
        else:
            print(f"✗ {response.message}\n")
    except Exception as e:
        print(f"✗ Error deleting chat session: {e}\n")

    print("=== All tests completed ===")


if __name__ == "__main__":
    test_chat_session_service()

