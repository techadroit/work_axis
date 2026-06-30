# tests/cache/test_message_cache.py
import datetime

import pytest

from src.app.server.cache.message_cache import get_message_cache
from src.app.server.messages.ChatMessages import ChatMessages, AgentMode, ChatMessageBody
from core.utils.time_util import get_utc_time


@pytest.fixture
def cache():
    """Create a fresh cache instance for each test"""
    cache_instance = get_message_cache()
    yield cache_instance
    cache_instance.clear()

@pytest.fixture
def sample_message():
    """Create a sample ChatMessages"""
    chat_message_body = ChatMessageBody(messages="Hello World")
    return ChatMessages(
        chat_session_id="chat_session_id",
        message_id="msg_123",
        utc_time=get_utc_time(),
        sender="assistant",
        receiver="user",
        message=chat_message_body,
        chat_mode=AgentMode.OFFLINE
    )


def test_add_message_to_cache(cache, sample_message):
    """Test adding a message to cache"""
    cache.add_or_update(sample_message.message_id, sample_message)

    retrieved = cache.get_message(sample_message.message_id)
    assert retrieved is not None
    assert retrieved.message_id == "msg_123"
    assert retrieved.message.messages == "Hello World"


def test_remove_message_from_cache(cache, sample_message):
    """Test removing a message from cache"""
    # Add message first
    cache.add_or_update(sample_message.message_id, sample_message)
    assert cache.has_message(sample_message.message_id)

    # Remove the message
    removed = cache.remove_message(sample_message.message_id)
    assert removed is not None
    assert removed.message_id == "msg_123"

    # Verify it's gone
    assert not cache.has_message(sample_message.message_id)
    assert cache.get_message(sample_message.message_id) is None


def test_add_multiple_messages_and_remove_one(cache):
    """Test adding multiple messages and removing one"""
    chat_message_body = ChatMessageBody(messages="Hello World")
    msg1 = ChatMessages(
        chat_session_id="chat_session_id",
        message_id="msg_123",
        utc_time=get_utc_time(),
        sender="assistant",
        receiver="user",
        message=chat_message_body,
        chat_mode=AgentMode.OFFLINE
    )

    chat_message_body = ChatMessageBody(messages="Hello World2")
    msg2 = ChatMessages(
        chat_session_id="chat_session_id",
        message_id="msg_1234",
        utc_time=get_utc_time(),
        sender="assistant",
        receiver="user",
        message=chat_message_body,
        chat_mode=AgentMode.OFFLINE
    )

    # Add both messages
    cache.add_or_update(msg1.message_id, msg1)
    cache.add_or_update(msg2.message_id, msg2)

    assert cache.has_message("msg_123")
    assert cache.has_message("msg_1234")

    # Remove only first message
    cache.remove_message("msg_123")

    assert not cache.has_message("msg_123")
    assert cache.has_message("msg_1234")  # Second message should still exist
