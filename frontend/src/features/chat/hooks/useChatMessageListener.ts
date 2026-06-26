import {useEffect} from 'react';
import {useChatDispatch} from '../stores/chatStore';
import {receiveWebSocketMessage} from '../stores/chatSlice';
import {MessageType, toChatMessageFromWebsocket} from '../types/chatMessage.types';
import {messageRouter} from '../utils/messageRouter';
import {logger} from '../../../core/logger';
import type {WebSocketMessage} from '../utils/messageHelpers';

/**
 * Hook to listen for chat messages (MessageType.MESSAGE)
 * Registers handler for MESSAGE type and updates chat store
 */
export function useChatMessageListener() {
    const chatDispatch = useChatDispatch();

    useEffect(() => {
        // Handler for MESSAGE type
        const handleChatMessage = (message: WebSocketMessage & { is_complete?: boolean; streaming?: boolean }) => {
            try {

                // Convert to ChatMessage format
                const chatMessage = toChatMessageFromWebsocket(message);

                // Determine if message is complete
                // For assistant messages: treat as streaming unless explicitly marked complete
                // For user messages: treat as complete (they don't stream)
                let isComplete: boolean;

                if (chatMessage.sender === chatMessage.receiver) {
                    // User's own message - always complete
                    isComplete = true;
                } else if (message.is_complete !== undefined) {
                    // Use explicit is_complete flag if present
                    isComplete = message.is_complete;
                } else if (message.streaming !== undefined) {
                    // Use streaming flag if present (inverted)
                    isComplete = !message.streaming;
                } else {
                    // No flags present - for assistant messages, treat as streaming
                    // This allows real-time updates
                    isComplete = chatMessage.sender !== 'assistant';
                }

                logger.info('Processing chat message', {
                    messageId: chatMessage.messageId,
                    sessionId: chatMessage.chatSessionId,
                    contentLength: chatMessage.message.messages.length,
                    is_complete: message.is_complete,
                    streaming: message.streaming,
                    isComplete,
                    sender: chatMessage.sender,
                });

                // Also log to console for easier debugging
                console.log('[CHAT MESSAGE]', {
                    messageId: chatMessage.messageId,
                    content: chatMessage.message.messages.substring(0, 50) + '...',
                    isComplete,
                    flags: { is_complete: message.is_complete, streaming: message.streaming },
                });

                // Dispatch to store with streaming state
                chatDispatch(receiveWebSocketMessage({
                    sessionId: chatMessage.chatSessionId,
                    message: chatMessage,
                    isComplete,
                }));
            } catch (error) {
                logger.error('Failed to process chat message', error, {message});
            }
        };

        // Register handler for MESSAGE type
        const unsubscribe = messageRouter.register(MessageType.MESSAGE, handleChatMessage);

        logger.info('Chat message listener registered');

        // Cleanup on unmount
        return () => {
            unsubscribe();
            logger.info('Chat message listener unregistered');
        };
    }, [chatDispatch]);
}

