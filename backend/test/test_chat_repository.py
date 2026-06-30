#!/usr/bin/env python3
"""Test script for ChatRepository CRUD operations"""

from src.app.server.database.repository.chat_session_repository import ChatSessionRepository
from src.app.server.database.models.chat_models import ChatCreate, ChatUpdate, MessageCreate


def test_chat_repository():
    print("Testing ChatRepository CRUD operations with Pydantic models...\n")
    
    # Test 1: Create a chat
    print("1. Creating a new chat...")
    chat_create = ChatCreate(user_id='test_user_1', title='Test Chat Session')
    chat_id = ChatSessionRepository.create_chat(chat_create)
    print(f"   ✅ Created chat with ID: {chat_id}\n")
    
    # Test 2: Retrieve the chat
    print("2. Retrieving the chat by ID...")
    chat = ChatSessionRepository.get_chat_by_id(chat_id)
    print(f"   ✅ Retrieved chat: {chat.title}")
    print(f"   User ID: {chat.user_id}")
    print(f"   Type: {type(chat).__name__}\n")
    
    # Test 3: Create messages
    print("3. Creating messages in the chat...")
    message_create_1 = MessageCreate(
        chat_id=chat_id,
        sender='user',
        receiver='ai',
        messages='Hello, AI! How are you?',
        mode='none'
    )
    # Test 6: Update chat
    print("6. Updating chat title...")
    chat_update = ChatUpdate(title="Updated Test Chat")
    ChatSessionRepository.update_chat(chat_id, chat_update)
    updated_chat = ChatSessionRepository.get_chat_by_id(chat_id)
    print(f"   ✅ New title: {updated_chat.title}\n")
    
    # Test 7: Get user chats
    print("7. Getting all chats for user...")
    user_chats = ChatSessionRepository.get_chats_by_user('test_user_1')
    print(f"   ✅ User has {len(user_chats)} chat(s)")
    print(f"   Type: List[{type(user_chats[0]).__name__}]\n")
    
    # Test 8: Archive chat
    print("8. Archiving the chat...")
    ChatSessionRepository.archive_chat(chat_id)
    archived_chat = ChatSessionRepository.get_chat_by_id(chat_id)
    print(f"   ✅ Chat archived: {archived_chat.is_archived}\n")
    
    # Test 9: Get user chats (should be 0 without archived)
    print("9. Getting active chats (should exclude archived)...")
    active_chats = ChatSessionRepository.get_chats_by_user('test_user_1', include_archived=False)
    print(f"   ✅ Active chats: {len(active_chats)}")
    archived_chats = ChatSessionRepository.get_chats_by_user('test_user_1', include_archived=True)
    print(f"   ✅ All chats (including archived): {len(archived_chats)}\n")
    
    # Test 10: Cleanup - Delete chat
    print("10. Cleaning up - deleting chat...")
    ChatSessionRepository.delete_chat(chat_id)
    deleted_chat = ChatSessionRepository.get_chat_by_id(chat_id)
    print(f"   ✅ Chat deleted (should be None): {deleted_chat}\n")
    
    print("=" * 60)
    print("🎉 All ChatRepository tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_chat_repository()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

