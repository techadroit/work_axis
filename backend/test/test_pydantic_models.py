#!/usr/bin/env python3
"""Test Pydantic models integration with ChatRepository"""

from src.app.server.database.repository.chat_session_repository import ChatSessionRepository
from src.app.server.database.models.chat_models import ChatCreate, MessageCreate, ChatUpdate

def test_pydantic_integration():
    print('Testing Pydantic Models Integration...\n')

    # Test 1: Create chat with model
    chat_create = ChatCreate(user_id='test_user', title='Test with Pydantic')
    chat_id = ChatSessionRepository.create_chat(chat_create)
    print(f'✅ Created chat: {chat_id}')

    # Test 2: Get chat (returns Chat model)
    chat = ChatSessionRepository.get_chat_by_id(chat_id)
    print(f'✅ Retrieved Chat model: {type(chat).__name__}')
    print(f'   Title: {chat.title}')
    print(f'   User: {chat.user_id}')

    # Test 3: Create message with model
    msg_create = MessageCreate(
        chat_id=chat_id,
        sender='user',
        receiver='ai',
        messages='Testing Pydantic!',
        mode='document'
    )
    msg_id = ChatSessionRepository.create_message(msg_create)
    print(f'✅ Created message: {msg_id}')

    # Test 4: Get message (returns Message model)
    message = ChatSessionRepository.get_message_by_id(msg_id)
    print(f'✅ Retrieved Message model: {type(message).__name__}')
    print(f'   Sender: {message.sender}')
    print(f'   Content: {message.messages}')

    # Test 5: Update chat with model
    update = ChatUpdate(title='Updated via Pydantic')
    ChatSessionRepository.update_chat(chat_id, update)
    updated = ChatSessionRepository.get_chat_by_id(chat_id)
    print(f'✅ Updated title: {updated.title}')

    # Test 6: Get chat with messages (returns ChatWithMessages)
    chat_full = ChatSessionRepository.get_chat_with_messages(chat_id)
    print(f'✅ ChatWithMessages model: {type(chat_full).__name__}')
    print(f'   Messages count: {len(chat_full.messages)}')
    print(f'   First message type: {type(chat_full.messages[0]).__name__}')

    # Test 7: Get chats with message count
    chats_count = ChatSessionRepository.get_chats_with_message_count('test_user')
    print(f'✅ ChatWithMessageCount models: {len(chats_count)}')
    print(f'   Message count: {chats_count[0].message_count}')

    # Cleanup
    ChatSessionRepository.delete_chat(chat_id)
    print(f'✅ Cleaned up')

    print('\n' + '='*60)
    print('🎉 All Pydantic model tests passed!')
    print('='*60)

if __name__ == '__main__':
    try:
        test_pydantic_integration()
    except Exception as e:
        print(f'\n❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        exit(1)

