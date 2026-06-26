import { useEffect, useState } from 'react';
import { useUserSelector } from '../stores/userStore';
import { messageService, ConnectionState } from '../../data/services';
import { logger } from '../../core/logger';

/**
 * Hook to manage WebSocket connection based on user authentication
 * Automatically connects when userId is available and disconnects on cleanup
 */
export function useWebSocketConnection() {
  const userId = useUserSelector((state) => state.user.userId);
  const [connectionState, setConnectionState] = useState<ConnectionState>(
    ConnectionState.DISCONNECTED
  );

  useEffect(() => {
    if (!userId) {
      logger.info('User ID not available, skipping WebSocket connection');
      return;
    }

    logger.info('Initializing WebSocket connection', { userId });

    // Subscribe to connection state changes
    const unsubscribeState = messageService.onStateChange((state) => {
      setConnectionState(state);
    });

    // Connect to WebSocket
    messageService.connect(userId);

    // Cleanup on unmount
    return () => {
      logger.info('Cleaning up WebSocket connection');
      unsubscribeState();
      messageService.disconnect();
    };
  }, [userId]);

  return {
    connectionState,
    isConnected: connectionState === ConnectionState.CONNECTED,
    sendMessage: (message: any) => messageService.sendMessage(message),
  };
}

