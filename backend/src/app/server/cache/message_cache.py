# server/cache/message_cache.py
from typing import Dict, Optional
import threading

from src.app.server.messages.ChatMessages import ChatMessages


class MessageCache:
    """Thread-safe cache for storing incomplete ChatMessage objects"""

    def __init__(self):
        self._cache: Dict[str, ChatMessages] = {}
        self._lock = threading.Lock()

    def add_or_update(self, message_id: str, chat_message: ChatMessages):
        """Add or update a ChatMessage in the cache"""
        with self._lock:
            if message_id in self._cache:
                # Append content to existing message
                existing = self._cache[message_id]
                existing.message.messages += chat_message.message.messages
                existing.utc_time = chat_message.utc_time  # Update timestamp
            else:
                # Store new message
                self._cache[message_id] = chat_message

    def get_message(self, message_id: str) -> Optional[ChatMessages]:
        """Get the complete ChatMessage from cache"""
        with self._lock:
            return self._cache.get(message_id)

    def remove_message(self, message_id: str) -> Optional[ChatMessages]:
        """Remove and return the ChatMessage from cache"""
        with self._lock:
            return self._cache.pop(message_id, None)

    def has_message(self, message_id: str) -> bool:
        """Check if message exists in cache"""
        with self._lock:
            return message_id in self._cache

    def clear(self):
        """Clear all cached messages"""
        with self._lock:
            self._cache.clear()


# Singleton instance
_message_cache = MessageCache()


def get_message_cache() -> MessageCache:
    """Get the singleton message cache instance"""
    return _message_cache
