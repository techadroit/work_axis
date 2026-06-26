import { apiClient } from '../../core/network/apiClient';
import type {
  ChatSessionCreateRequest,
  ChatSessionCreateResponse,
  ChatSessionResponse,
  ChatSessionUpdateRequest,
  ChatSessionUpdateResponse,
  ChatSessionListResponse,
} from '../../features/chat/types/chatSession.types';

/**
 * Chat Session API - API calls related to chat session operations
 * Equivalent to ChatSessionRepository in Kotlin
 */
export class ChatSessionApi {
  /**
   * Create a new chat session
   */
  static async createChatSession(request: ChatSessionCreateRequest): Promise<ChatSessionCreateResponse> {
    return apiClient.post<ChatSessionCreateResponse>('/api/chat/sessions', request);
  }

  /**
   * Get a specific chat session by ID
   */
  static async getChatSession(chatSessionId: string): Promise<ChatSessionResponse> {
    return apiClient.get<ChatSessionResponse>(`/api/chat/sessions/${chatSessionId}`);
  }

  /**
   * Update chat session
   */
  static async updateChatSession(
    chatSessionId: string,
    request: ChatSessionUpdateRequest
  ): Promise<ChatSessionUpdateResponse> {
    return apiClient.put<ChatSessionUpdateResponse>(`/api/chat/sessions/${chatSessionId}`, request);
  }

  /**
   * Permanently delete a chat session and all its messages
   */
  static async deleteChatSession(chatSessionId: string): Promise<ChatSessionUpdateResponse> {
    return apiClient.delete<ChatSessionUpdateResponse>(`/api/chat/sessions/${chatSessionId}`);
  }

  /**
   * Get all chat sessions for a user
   */
  static async getUserChatSessions(
    _userId: string,
    includeArchived: boolean = false
  ): Promise<ChatSessionListResponse> {
    return apiClient.get<ChatSessionListResponse>(`/api/chat/users/${_userId}/sessions`, {
    // return apiClient.get<ChatSessionListResponse>(`/api/chat/users/3b97b6e9-ab2f-4f90-8469-4d53aedcddc4/sessions`, {
      params: { include_archived: includeArchived.toString() }
    });
  }

  /**
   * Archive a chat session
   */
  static async archiveChatSession(chatSessionId: string): Promise<ChatSessionUpdateResponse> {
    return apiClient.put<ChatSessionUpdateResponse>(`/api/chat/sessions/${chatSessionId}/archive`);
  }
}

