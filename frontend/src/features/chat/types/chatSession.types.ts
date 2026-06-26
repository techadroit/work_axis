// Request Models

/**
 * Chat Session Create Request
 */
export interface ChatSessionCreateRequest {
  user_id: string;
  title?: string | null;
}

/**
 * Chat Session Update Request
 */
export interface ChatSessionUpdateRequest {
  title?: string | null;
  is_archived?: boolean | null;
}

// Response Models

/**
 * Chat Session Create Response
 */
export interface ChatSessionCreateResponse {
  chat_session_id: string;
  title: string;
  message: string;
}

/**
 * Chat Session Response
 */
export interface ChatSessionResponse {
  chat_session_id: string;
  user_id: string;
  title?: string | null;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
}

/**
 * Chat Session List Response
 */
export interface ChatSessionListResponse {
  chat_sessions: ChatSessionResponse[];
  count: number;
}

/**
 * Chat Session Update Response
 */
export interface ChatSessionUpdateResponse {
  success: boolean;
  message: string;
  data?: Record<string, string> | null;
}

// Domain Models (for app usage)

/**
 * Chat Session - Domain model
 */
export interface ChatSession {
  chatSessionId: string;
  userId: string;
  title?: string | null;
  createdAt: string;
  updatedAt: string;
  isArchived: boolean;
}

// Mapper function
export const toChatSession = (response: ChatSessionResponse): ChatSession => ({
  chatSessionId: response.chat_session_id,
  userId: response.user_id,
  title: response.title,
  createdAt: response.created_at,
  updatedAt: response.updated_at,
  isArchived: response.is_archived,
});

