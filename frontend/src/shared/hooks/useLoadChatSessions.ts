import { createAsyncThunk } from '@reduxjs/toolkit';
import { ChatSessionService } from '../../data/services/ChatSessionService';
import { logger } from '../../core/logger';

/**
 * Async thunk to load chat sessions
 * Delegates business logic to ChatSessionService
 */
export const loadChatSessions = createAsyncThunk(
  'chatSession/loadSessions',
  async (userId: string, { rejectWithValue }) => {
    try {
      logger.addBreadcrumb('Starting chat sessions load', { userId });
      const chatSessionService = new ChatSessionService();
      const sessions = await chatSessionService.getAllSessions(userId);
      logger.info('Chat sessions load completed', {
        userId,
        sessionCount: sessions.length
      });
      return sessions;
    } catch (error) {
      logger.error('Failed to load chat sessions', error, { userId });
      return rejectWithValue(
        error instanceof Error ? error.message : 'Failed to load chat sessions'
      );
    }
  }
);

