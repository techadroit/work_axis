import { ChatSessionApi } from '../api/ChatSessionApi';
import type { ChatSession } from '../../features/chat/types/chatSession.types';
import { toChatSession } from '../../features/chat/types/chatSession.types';
import { logger } from '../../core/logger';

/**
 * ChatSessionService - Business logic for chat session operations
 */
export class ChatSessionService {
  /**
   * Get all chat sessions for a user
   */
  async getAllSessions(userId: string, includeArchived: boolean = false): Promise<ChatSession[]> {
    try {
      logger.info('Fetching all chat sessions', { userId, includeArchived });
      const response = await ChatSessionApi.getUserChatSessions(userId, includeArchived);

      // Map API response to domain models
      const sessions = response.chat_sessions.map(toChatSession);

      logger.info('Chat sessions fetched successfully', {
        userId,
        count: sessions.length
      });

      return sessions;
    } catch (error) {
      logger.error('Failed to fetch chat sessions', error, { userId });
      throw error;
    }
  }

  /**
   * Create a new chat session
   */
  async createSession(userId: string, title?: string): Promise<string> {
    try {
      logger.info('Creating chat session', { userId, title });
      const response = await ChatSessionApi.createChatSession({ user_id: userId, title });
      logger.info('Chat session created', { sessionId: response.chat_session_id });
      return response.chat_session_id;
    } catch (error) {
      logger.error('Failed to create chat session', error, { userId });
      throw error;
    }
  }

  /**
   * Update a chat session
   */
  async updateSession(sessionId: string, updates: { title?: string; is_archived?: boolean }): Promise<void> {
    try {
      logger.info('Updating chat session', { sessionId, updates });
      await ChatSessionApi.updateChatSession(sessionId, updates);
      logger.info('Chat session updated', { sessionId });
    } catch (error) {
      logger.error('Failed to update chat session', error, { sessionId });
      throw error;
    }
  }

  /**
   * Delete a chat session
   */
  async deleteSession(sessionId: string): Promise<void> {
    try {
      logger.info('Deleting chat session', { sessionId });
      await ChatSessionApi.deleteChatSession(sessionId);
      logger.info('Chat session deleted', { sessionId });
    } catch (error) {
      logger.error('Failed to delete chat session', error, { sessionId });
      throw error;
    }
  }

  /**
   * Archive a chat session
   */
  async archiveSession(sessionId: string): Promise<void> {
    try {
      logger.info('Archiving chat session', { sessionId });
      await ChatSessionApi.archiveChatSession(sessionId);
      logger.info('Chat session archived', { sessionId });
    } catch (error) {
      logger.error('Failed to archive chat session', error, { sessionId });
      throw error;
    }
  }
}
