import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import type { ChatMessage } from '../types/chatMessage.types';
import { ChatMessageApi } from '../../../data/api/ChatMessageApi';
import { toChatMessage } from '../types/chatMessage.types';
import { logger } from '../../../core/logger';
import { apiClient } from '../../../core/network/apiClient';

interface PaginationInfo {
  currentPage: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
  totalCount: number;
}

interface ChatState {
  messagesByChatSession: Record<string, ChatMessage[]>;
  streamingMessagesByChatSession: Record<string, ChatMessage[]>; // Store streaming messages separately
  paginationByChatSession: Record<string, PaginationInfo>;
  loading: boolean;
  loadingMore: boolean; // For pagination loading
  error: string | null;
  sendingMessage: boolean;
  isTyping: boolean; // Track if assistant is typing
}

const initialState: ChatState = {
  messagesByChatSession: {},
  streamingMessagesByChatSession: {},
  paginationByChatSession: {},
  loading: false,
  loadingMore: false,
  error: null,
  sendingMessage: false,
  isTyping: false,
};

/**
 * Load messages for a specific chat session
 */
export const loadMessages = createAsyncThunk(
  'chat/loadMessages',
  async (
    { sessionId, pageNo = 0, pageSize = 20 }: { sessionId: string; pageNo?: number; pageSize?: number },
    { rejectWithValue }
  ) => {
    try {
      logger.info('Loading messages for session', { sessionId, pageNo, pageSize });
      const response = await ChatMessageApi.getAllMessages(sessionId, pageNo, pageSize);

      // Backend commonly returns newest-first; render expects oldest-first.
      const messages = response.messages.map(toChatMessage).reverse();

      return {
        sessionId,
        messages,
        pageNo,
        pagination: {
          currentPage: response.page,
          totalPages: response.total_pages,
          hasNext: response.has_next,
          hasPrevious: response.has_previous,
          totalCount: response.total_count,
        },
      };
    } catch (error) {
      logger.error('Failed to load messages', error);
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load messages');
    }
  }
);

/**
 * Send a new message
 */
export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (
    { sessionId, message, sender, receiver }: {
      sessionId: string;
      message: string;
      sender: string;
      receiver: string;
    },
    { rejectWithValue }
  ) => {
    try {
      logger.info('Sending message', { sessionId, sender, receiver });

      // Send message to API
      const response = await apiClient.post<any>(`/api/messages/${sessionId}`, {
        messages: message,
        sender,
        receiver,
        mode: 'offline',
      });

      // Map response to ChatMessage
      const newMessage = toChatMessage(response);
      return { sessionId, message: newMessage };
    } catch (error) {
      logger.error('Failed to send message', error);
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to send message');
    }
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    clearMessages: (state, action: PayloadAction<string>) => {
      const sessionId = action.payload;
      delete state.messagesByChatSession[sessionId];
      delete state.streamingMessagesByChatSession[sessionId];
      logger.info('Messages cleared for session', { sessionId });
    },
    addMessageOptimistically: (state, action: PayloadAction<{ sessionId: string; message: ChatMessage }>) => {
      const { sessionId, message } = action.payload;
      if (!state.messagesByChatSession[sessionId]) {
        state.messagesByChatSession[sessionId] = [];
      }
      state.messagesByChatSession[sessionId].push(message);
    },
    receiveWebSocketMessage: (state, action: PayloadAction<{ sessionId: string; message: ChatMessage; isComplete?: boolean }>) => {
      const { sessionId, message, isComplete = false } = action.payload;

      // Initialize arrays if needed
      if (!state.messagesByChatSession[sessionId]) {
        state.messagesByChatSession[sessionId] = [];
      }
      if (!state.streamingMessagesByChatSession[sessionId]) {
        state.streamingMessagesByChatSession[sessionId] = [];
      }

      // Clear typing indicator when receiving a message from assistant
      if (message.sender === 'assistant' || message.sender !== message.receiver) {
        state.isTyping = false;
      }

      if (isComplete) {
        // Message is complete - move it to main messages

        // First, check if it's in streaming messages (update it there)
        const streamingIndex = state.streamingMessagesByChatSession[sessionId].findIndex(
          m => m.messageId === message.messageId
        );

        if (streamingIndex !== -1) {
          // Get the final streaming message
          const finalStreamingMessage = state.streamingMessagesByChatSession[sessionId][streamingIndex];

          // Append any remaining content from the completion message
          const completeMessage = {
            ...finalStreamingMessage,
            message: {
              messages: finalStreamingMessage.message.messages + message.message.messages
            },
            utcTime: message.utcTime,
          };

          // Remove from streaming messages
          state.streamingMessagesByChatSession[sessionId].splice(streamingIndex, 1);

          // Add to main messages if not already there
          const existsInMain = state.messagesByChatSession[sessionId].some(
            m => m.messageId === message.messageId
          );

          if (!existsInMain) {
            state.messagesByChatSession[sessionId].push(completeMessage);
            console.log('[STREAMING] Message completed and added to main messages:', {
              sessionId,
              messageId: message.messageId,
              finalLength: completeMessage.message.messages.length,
            });
          } else {
            console.log('[STREAMING] Message already exists in main messages, skipping:', {
              sessionId,
              messageId: message.messageId,
            });
          }

          logger.info('Streaming message completed and moved to main messages', {
            sessionId,
            messageId: message.messageId,
            finalLength: completeMessage.message.messages.length,
          });
        } else {
          // Message wasn't streaming, just add it directly to main messages
          const existsInMain = state.messagesByChatSession[sessionId].some(
            m => m.messageId === message.messageId
          );

          if (!existsInMain) {
            state.messagesByChatSession[sessionId].push(message);
            logger.info('Complete message added directly to main messages', {
              sessionId,
              messageId: message.messageId,
            });
          }
        }
      } else {
        // Message is streaming - keep it in streaming messages
        const streamingIndex = state.streamingMessagesByChatSession[sessionId].findIndex(
          m => m.messageId === message.messageId
        );

        if (streamingIndex !== -1) {
          // Update existing streaming message (append content)
          const existingMessage = state.streamingMessagesByChatSession[sessionId][streamingIndex];
          const updatedMessage = {
            ...existingMessage,
            message: {
              messages: existingMessage.message.messages + message.message.messages
            },
            utcTime: message.utcTime,
          };

          // Create new array to ensure selector detects the change
          state.streamingMessagesByChatSession[sessionId] = [
            ...state.streamingMessagesByChatSession[sessionId].slice(0, streamingIndex),
            updatedMessage,
            ...state.streamingMessagesByChatSession[sessionId].slice(streamingIndex + 1)
          ];

          console.log('[STREAMING] Message updated:', {
            sessionId,
            messageId: message.messageId,
            currentLength: updatedMessage.message.messages.length,
            content: updatedMessage.message.messages.substring(0, 100),
          });

          logger.info('Streaming message updated', {
            sessionId,
            messageId: message.messageId,
            currentLength: updatedMessage.message.messages.length,
          });
        } else {
          // New streaming message
          state.streamingMessagesByChatSession[sessionId].push(message);

          console.log('[STREAMING] New message started:', {
            sessionId,
            messageId: message.messageId,
            content: message.message.messages.substring(0, 50),
            totalStreamingMessages: state.streamingMessagesByChatSession[sessionId].length,
          });

          logger.info('New streaming message started', {
            sessionId,
            messageId: message.messageId,
          });
        }
      }
    },
    markMessageComplete: (state, action: PayloadAction<{ sessionId: string; messageId: string }>) => {
      const { sessionId, messageId } = action.payload;

      if (!state.streamingMessagesByChatSession[sessionId]) {
        return;
      }

      // Find the streaming message
      const streamingIndex = state.streamingMessagesByChatSession[sessionId].findIndex(
        m => m.messageId === messageId
      );

      if (streamingIndex !== -1) {
        // Move from streaming to main messages
        const streamingMessage = state.streamingMessagesByChatSession[sessionId][streamingIndex];

        // Remove from streaming
        state.streamingMessagesByChatSession[sessionId].splice(streamingIndex, 1);

        // Add to main messages if not already there
        if (!state.messagesByChatSession[sessionId]) {
          state.messagesByChatSession[sessionId] = [];
        }

        const existsInMain = state.messagesByChatSession[sessionId].some(
          m => m.messageId === messageId
        );

        if (!existsInMain) {
          state.messagesByChatSession[sessionId].push(streamingMessage);
        }

        logger.info('Message marked as complete and moved to main messages', { sessionId, messageId });
      }
    },
    setTyping: (state, action: PayloadAction<boolean>) => {
      state.isTyping = action.payload;
      logger.info('Typing indicator state changed', { isTyping: action.payload });
    },
  },
  extraReducers: (builder) => {
    // Load messages
    builder
      .addCase(loadMessages.pending, (state, action) => {
        const { pageNo } = action.meta.arg;
        // Use loadingMore for pagination (pageNo > 0), loading for initial load
        if (pageNo === 0) {
          state.loading = true;
        } else {
          state.loadingMore = true;
        }
        state.error = null;
      })
      .addCase(loadMessages.fulfilled, (state, action) => {
        state.loading = false;
        state.loadingMore = false;

        const { sessionId, messages, pageNo, pagination } = action.payload;

        // Store pagination info
        state.paginationByChatSession[sessionId] = pagination;

        if (pageNo === 0 || !state.messagesByChatSession[sessionId]) {
          state.messagesByChatSession[sessionId] = messages;
          // Clear streaming messages when loading fresh messages (pageNo === 0)
          // This prevents duplicates when revisiting a session
          if (pageNo === 0) {
            const hadStreamingMessages = state.streamingMessagesByChatSession[sessionId]?.length > 0;
            state.streamingMessagesByChatSession[sessionId] = [];
            if (hadStreamingMessages) {
              console.log('[LOAD MESSAGES] Cleared streaming messages on fresh load:', {
                sessionId,
                previousStreamingCount: hadStreamingMessages,
              });
            }
          }
        } else {
          const existing = state.messagesByChatSession[sessionId];
          const existingIds = new Set(existing.map(m => m.messageId));
          const olderDeduped = messages.filter(m => !existingIds.has(m.messageId));
          // Prepend older messages (they come from earlier pages)
          state.messagesByChatSession[sessionId] = [...olderDeduped, ...existing];
        }

        logger.info('Messages loaded successfully', {
          sessionId,
          count: state.messagesByChatSession[sessionId].length,
          pageNo,
          pagination,
        });
      })
      .addCase(loadMessages.rejected, (state, action) => {
        state.loading = false;
        state.loadingMore = false;
        state.error = action.payload as string;
        logger.error('Failed to load messages', { error: action.payload });
      });

    // Send message
    builder
      .addCase(sendMessage.pending, (state) => {
        state.sendingMessage = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.sendingMessage = false;
        const { sessionId, message } = action.payload;

        // Add message to the list if it doesn't exist
        if (!state.messagesByChatSession[sessionId]) {
          state.messagesByChatSession[sessionId] = [];
        }

        // Check if message already exists (optimistic update)
        const exists = state.messagesByChatSession[sessionId].some(
          m => m.messageId === message.messageId
        );

        if (!exists) {
          state.messagesByChatSession[sessionId].push(message);
        }

        logger.info('Message sent successfully', {
          sessionId,
          messageId: message.messageId
        });
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.sendingMessage = false;
        state.error = action.payload as string;
        logger.error('Failed to send message', { error: action.payload });
      });
  },
});

export const { clearMessages, addMessageOptimistically, receiveWebSocketMessage, markMessageComplete, setTyping } = chatSlice.actions;
export default chatSlice.reducer;

