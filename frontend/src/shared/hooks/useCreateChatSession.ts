import { createAsyncThunk } from '@reduxjs/toolkit';
import { ChatSessionService } from '../../data/services/ChatSessionService';
import { logger } from '../../core/logger';

interface CreateChatSessionParams {
  userId: string;
  title?: string;
}

/**
 * Async thunk to create a new chat session
 * Delegates business logic to ChatSessionService
 * Returns the newly created session ID
 */
export const createChatSession = createAsyncThunk(
  'chatSession/createSession',
  async ({ userId, title }: CreateChatSessionParams, { rejectWithValue }) => {
    try {
      logger.addBreadcrumb('Starting chat session creation', { userId, title });
      const chatSessionService = new ChatSessionService();
      const sessionId = await chatSessionService.createSession(userId, title);
      logger.info('Chat session created successfully', {
        userId,
        sessionId
      });
      return sessionId;
    } catch (error) {
      logger.error('Failed to create chat session', error, { userId });
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to create chat session'
      );
    }
  }
);

