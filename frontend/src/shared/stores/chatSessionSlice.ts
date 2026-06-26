import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { ChatSession } from '../../features/chat/types/chatSession.types';
import { loadChatSessions } from '../hooks/useLoadChatSessions';
import { createChatSession } from '../hooks/useCreateChatSession';
import { logger } from '../../core/logger';

interface ChatSessionState {
  sessions: ChatSession[];
  loading: boolean;
  error: string | null;
  selectedSessionId: string | null;
  creatingSession: boolean;
  createError: string | null;
  newSessionId: string | null;
}

const initialState: ChatSessionState = {
  sessions: [],
  loading: false,
  error: null,
  selectedSessionId: null,
  creatingSession: false,
  createError: null,
  newSessionId: null,
};

const chatSessionSlice = createSlice({
  name: 'chatSession',
  initialState,
  reducers: {
    addSession: (state, action: PayloadAction<ChatSession>) => {
      state.sessions.unshift(action.payload);
      logger.info('Chat session added', { sessionId: action.payload.chatSessionId });
    },
    updateSession: (state, action: PayloadAction<ChatSession>) => {
      const index = state.sessions.findIndex(
        s => s.chatSessionId === action.payload.chatSessionId
      );
      if (index !== -1) {
        state.sessions[index] = action.payload;
        logger.info('Chat session updated', { sessionId: action.payload.chatSessionId });
      }
    },
    removeSession: (state, action: PayloadAction<string>) => {
      state.sessions = state.sessions.filter(
        s => s.chatSessionId !== action.payload
      );
      logger.info('Chat session removed', { sessionId: action.payload });

      // Clear selected session if it was deleted
      if (state.selectedSessionId === action.payload) {
        state.selectedSessionId = null;
      }
    },
    selectSession: (state, action: PayloadAction<string>) => {
      state.selectedSessionId = action.payload;
      logger.addBreadcrumb('Chat session selected', { sessionId: action.payload });
    },
    updateSessionTitle: (state, action: PayloadAction<{ sessionId: string; title: string }>) => {
      const { sessionId, title } = action.payload;
      const session = state.sessions.find(s => s.chatSessionId === sessionId);
      if (session) {
        session.title = title;
      }
    },
    clearSessions: (state) => {
      state.sessions = [];
      state.selectedSessionId = null;
      logger.info('Chat sessions cleared');
    },
  },
  extraReducers: (builder) => {
    builder
      // Load Chat Sessions
      .addCase(loadChatSessions.pending, (state) => {
        logger.addBreadcrumb('loadChatSessions.pending', { loading: true });
        state.loading = true;
        state.error = null;
      })
      .addCase(loadChatSessions.fulfilled, (state, action: PayloadAction<ChatSession[]>) => {
        logger.addBreadcrumb('loadChatSessions.fulfilled', {
          count: action.payload.length
        });
        state.loading = false;
        state.sessions = action.payload;
        state.error = null;
      })
      .addCase(loadChatSessions.rejected, (state, action) => {
        logger.error('loadChatSessions.rejected', undefined, {
          error: action.payload
        });
        state.loading = false;
        state.error = action.payload as string;
      })
      // Create Chat Session
      .addCase(createChatSession.pending, (state) => {
        logger.addBreadcrumb('createChatSession.pending', { creatingSession: true });
        state.creatingSession = true;
        state.createError = null;
        state.newSessionId = null;
      })
      .addCase(createChatSession.fulfilled, (state, action: PayloadAction<string>) => {
        logger.addBreadcrumb('createChatSession.fulfilled', {
          sessionId: action.payload
        });
        state.creatingSession = false;
        state.newSessionId = action.payload;
        state.selectedSessionId = action.payload;
        state.createError = null;
      })
      .addCase(createChatSession.rejected, (state, action) => {
        logger.error('createChatSession.rejected', undefined, {
          error: action.payload
        });
        state.creatingSession = false;
        state.createError = action.payload as string;
      });
  },
});

export const {
  addSession,
  updateSession,
  removeSession,
  selectSession,
  updateSessionTitle,
  clearSessions
} = chatSessionSlice.actions;
export default chatSessionSlice.reducer;

