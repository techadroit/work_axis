import { MessageType } from '../types/chatMessage.types';
import type { WebSocketMessage } from '../utils/messageHelpers';
import {logger} from "../../../core/logger";

/**
 * Message handler function type
 */
export type MessageHandler = (message: WebSocketMessage) => void;

/**
 * WebSocket Message Router
 * Routes messages to appropriate handlers based on message_type
 */
class WebSocketMessageRouter {
  private handlers: Map<MessageType, Set<MessageHandler>> = new Map();

  /**
   * Register a handler for a specific message type
   */
  register(messageType: MessageType, handler: MessageHandler): () => void {
    if (!this.handlers.has(messageType)) {
      this.handlers.set(messageType, new Set());
    }

    this.handlers.get(messageType)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.unregister(messageType, handler);
    };
  }

  /**
   * Unregister a handler for a specific message type
   */
  unregister(messageType: MessageType, handler: MessageHandler): void {
    const handlers = this.handlers.get(messageType);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.handlers.delete(messageType);
      }
    }
  }

  /**
   * Route a message to all registered handlers for its type
   */
  route(message: WebSocketMessage): void {
    const messageType = message.message_type as MessageType;
    const handlers = this.handlers.get(messageType);

    if (handlers && handlers.size > 0) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          logger.error(`Error in message handler for type ${messageType}:`, error);
        }
      });
    } else {
      logger.warn(`No handlers registered for message type: ${messageType}`);
    }
  }

  /**
   * Get all registered message types
   */
  getRegisteredTypes(): MessageType[] {
    return Array.from(this.handlers.keys());
  }

  /**
   * Clear all handlers
   */
  clear(): void {
    this.handlers.clear();
  }
}

// Export singleton instance
export const messageRouter = new WebSocketMessageRouter();

