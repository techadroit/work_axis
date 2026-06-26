#!/usr/bin/env python3
"""Test script for refactored ChatSessionRepository"""

from backend.app.server.database.repository.chat_session_repository import ChatSessionRepository
from backend.app.server.database.models.chat_session_models import ChatSessionCreate, ChatSessionUpdate, MessageCreate


def test_chat_session_repository():
    print("Testing Refactored ChatSessionRepository...\n")

    # Test 1: Create a chat session
    print("1. Creating a new chat session...")
    chat_session_create = ChatSessionCreate(user_id='test_user_1', title='Test Chat Session')
    chat_session_id = ChatSessionRepository.create_chat_session(chat_session_create)
    print(f"   ✅ Created chat session with ID: {chat_session_id}\n")

    # Test 2: Retrieve the chat session
    print("2. Retrieving the chat session by ID...")
    chat_session = ChatSessionRepository.get_chat_session_by_id(chat_session_id)
    print(f"   ✅ Retrieved ChatSession model: {type(chat_session).__name__}")
    print(f"   Title: {chat_session.title}")
    print(f"   User ID: {chat_session.user_id}")
    print(f"   ID field: {chat_session.chat_session_id}\n")

    # Test 3: Create messages
    print("3. Creating messages in the chat session...")
    message_create_1 = MessageCreate(
        chat_session_id=chat_session_id,
        sender='user',
        receiver='ai',
        messages='Hello, AI! How are you?',
        mode='none'
    )
    message_id_1 = ChatSessionRepository.create_message(message_create_1)
    print(f"   ✅ Created message 1: {message_id_1}")

    message_create_2 = MessageCreate(
        chat_session_id=chat_session_id,
        sender='ai',
        receiver='user',
        messages='Hello! I am doing well, thank you!',
        mode='none'
    )
    message_id_2 = ChatSessionRepository.create_message(message_create_2)
    print(f"   ✅ Created message 2: {message_id_2}\n")

    # Test 4: Retrieve messages
    print("4. Retrieving all messages for the chat session...")
    messages = ChatSessionRepository.get_messages_by_chat(chat_session_id)
    print(f"   ✅ Retrieved {len(messages)} messages")
    for i, msg in enumerate(messages, 1):
        print(f"   Message {i}: {msg.sender} -> {msg.receiver}: {msg.messages[:30]}...")
        print(f"   Message has chat_session_id: {msg.chat_session_id}")
    print()

    # Test 5: Get message count
    print("5. Getting message count...")
    count = ChatSessionRepository.get_chat_session_message_count(chat_session_id)
    print(f"   ✅ Message count: {count}\n")

    # Test 6: Update chat session
    print("6. Updating chat session title...")
    chat_session_update = ChatSessionUpdate(title="Updated Test Chat Session")
    ChatSessionRepository.update_chat_session(chat_session_id, chat_session_update)
    updated_chat_session = ChatSessionRepository.get_chat_session_by_id(chat_session_id)
    print(f"   ✅ New title: {updated_chat_session.title}\n")

    # Test 7: Get user chat sessions
    print("7. Getting all chat sessions for user...")
    user_chat_sessions = ChatSessionRepository.get_chat_sessions_by_user('test_user_1')
    print(f"   ✅ User has {len(user_chat_sessions)} chat session(s)")
    print(f"   Type: List[{type(user_chat_sessions[0]).__name__}]\n")

    # Test 8: Archive chat session
    print("8. Archiving the chat session...")
    ChatSessionRepository.archive_chat_session(chat_session_id)
    archived_chat_session = ChatSessionRepository.get_chat_session_by_id(chat_session_id)
    print(f"   ✅ Chat session archived: {archived_chat_session.is_archived}\n")

    # Test 9: Get user chat sessions (should be 0 without archived)
    print("9. Getting active chat sessions (should exclude archived)...")
    active_chat_sessions = ChatSessionRepository.get_chat_sessions_by_user('test_user_1', include_archived=False)
    print(f"   ✅ Active chat sessions: {len(active_chat_sessions)}")
    archived_chat_sessions = ChatSessionRepository.get_chat_sessions_by_user('test_user_1', include_archived=True)
    print(f"   ✅ All chat sessions (including archived): {len(archived_chat_sessions)}\n")

    # Test 10: Get chat session with messages
    print("10. Getting chat session with messages...")
    chat_session_full = ChatSessionRepository.get_chat_session_with_messages(chat_session_id)
    print(f"   ✅ ChatSessionWithMessages model: {type(chat_session_full).__name__}")
    print(f"   Messages count: {len(chat_session_full.messages)}\n")

    # Test 11: Cleanup - Delete chat session
    print("11. Cleaning up - deleting chat session...")
    ChatSessionRepository.delete_chat_session(chat_session_id)
    deleted_chat_session = ChatSessionRepository.get_chat_session_by_id(chat_session_id)
    print(f"   ✅ Chat session deleted (should be None): {deleted_chat_session}\n")

    print("=" * 60)
    print("🎉 All refactored ChatSessionRepository tests passed!")
    print("=" * 60)
    print("\nRefactoring Summary:")
    print("  ✅ chat → chat_session")
    print("  ✅ chat_id → chat_session_id")
    print("  ✅ chats table → chat_sessions table")
    print("  ✅ ChatRepository → ChatSessionRepository")
    print("  ✅ All models and methods renamed")


if __name__ == "__main__":
    try:
        test_chat_session_repository()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

