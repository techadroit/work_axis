import { useEffect } from 'react';
import { useChatSessionDispatch } from '../stores/chatSessionStore';
import { updateSessionTitle } from '../stores/chatSessionSlice';
import { MessageType } from '../../features/chat/types/chatMessage.types';
import { messageRouter } from '../../features/chat/utils/messageRouter';
import { logger } from '../../core/logger';
import type { WebSocketMessage } from '../../features/chat/utils/messageHelpers';

/**
 * Hook to listen for title update messages (MessageType.UPDATE_TITLE)
 * Updates chat session title in the navigation drawer
 */
export function useTitleUpdateListener() {
  const chatSessionDispatch = useChatSessionDispatch();

  useEffect(() => {
    // Handler for UPDATE_TITLE type
    const handleTitleUpdate = (message: WebSocketMessage) => {
      try {
        // Validate message fields
        if (!message.chat_session_id) {
          logger.error('Title update message missing chat_session_id', undefined, { message });
          return;
        }

        if (!message.message?.messages) {
          logger.error('Title update message missing title content', undefined, { message });
          return;
        }

        const sessionId = message.chat_session_id;
        const newTitle = message.message.messages;

        logger.info('Processing title update', {
          sessionId,
          newTitle
        });

        // Update session title in store
        chatSessionDispatch(updateSessionTitle({
          sessionId,
          title: newTitle,
        }));
      } catch (error) {
        logger.error('Failed to process title update', error, { message });
      }
    };

    // Register handler for UPDATE_TITLE type
    const unsubscribe = messageRouter.register(MessageType.UPDATE_TITLE, handleTitleUpdate);

    logger.info('Title update listener registered');

    // Cleanup on unmount
    return () => {
      unsubscribe();
      logger.info('Title update listener unregistered');
    };
  }, [chatSessionDispatch]);
}

