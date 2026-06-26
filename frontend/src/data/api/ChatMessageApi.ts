import { apiClient } from '../../core/network/apiClient.ts';
import type { PaginatedChatResponse } from '../../features/chat/types/chatMessage.types.ts';

/**
 * Chat Message API - API calls related to chat message operations
 * Equivalent to ChatMessageRepository in Kotlin
 */
export class ChatMessageApi {
  /**
   * Get all messages for a chat session
   */
  static async getAllMessages(
    sessionId: string,
    page_no: number = 0,
    page_size: number = 20
  ): Promise<PaginatedChatResponse> {
    const params = new URLSearchParams({
      page_no: String(page_no),
      page_size: String(page_size),
    });

    return apiClient.get<PaginatedChatResponse>(
      `/api/messages/${sessionId}?${params.toString()}`
    );
  }
}
