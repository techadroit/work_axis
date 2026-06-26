import { useEffect } from 'react';
import { messageService } from '../../data/services';
import { messageRouter } from '../../features/chat/utils/messageRouter';
import { logger } from '../../core/logger';
import type { WebSocketMessage } from '../../features/chat/utils/messageHelpers';

/**
 * Global WebSocket listener hook
 * Routes incoming messages to registered handlers based on message_type
 * Should be mounted once at app level (e.g., in MainScreen or App)
 */
export function useGlobalWebSocketListener() {
  useEffect(() => {
    logger.info('Global WebSocket listener initialized');

    // Subscribe to all WebSocket messages
    const unsubscribe = messageService.onMessage((message: WebSocketMessage) => {
      try {
        logger.info(`Received WebSocket message in global listener`, { message });

        // Validate required fields
        if (!message.message_id || !message.chat_session_id) {
          logger.error('WebSocket message missing required fields', undefined, { message });
          return;
        }

        // Route message to appropriate handlers
        messageRouter.route(message);
      } catch (error) {
        logger.error('Failed to route WebSocket message', error, { message });
      }
    });

    // Cleanup subscription on unmount
    return () => {
      logger.info('Global WebSocket listener cleanup');
      unsubscribe();
    };
  }, []);
}

