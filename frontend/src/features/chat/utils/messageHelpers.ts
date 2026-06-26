import { ChatModeType, MessageType, ContentType } from '../types/chatMessage.types';
import { utcNowIso } from '../../../util/TimeUtil';

/**
 * WebSocket message format interface
 */
export interface WebSocketMessage {
  message_id: string;
  utc_time: string;
  chat_session_id: string;
  sender: string;
  receiver: string;
  message: {
    messages: string;
  };
  chat_mode: string;
  message_type: string;
  content_type: string;
  file_name: string;
  file_type: string;
  file_path: string;
}

/**
 * Generate a unique message ID using timestamp in milliseconds
 */
export const generateMessageId = (): string => {
  return Date.now().toString();
};

/**
 * Get current UTC time in ISO format
 */
export const getCurrentUtcTime = (): string => {
  return utcNowIso();
};

/**
 * Create a WebSocket message payload
 */
export const createWebSocketMessage = ({
  sessionId,
  message,
  sender,
  receiver,
  chatMode = ChatModeType.AGENT,
  messageType = MessageType.MESSAGE,
  contentType = ContentType.TEXT,
  fileName = '',
  fileType = '',
  filePath = '',
}: {
  sessionId: string;
  message: string;
  sender: string;
  receiver: string;
  chatMode?: ChatModeType;
  messageType?: MessageType;
  contentType?: ContentType;
  fileName?: string;
  fileType?: string;
  filePath?: string;
}): WebSocketMessage => {
  return {
    message_id: generateMessageId(),
    utc_time: getCurrentUtcTime(),
    chat_session_id: sessionId,
    sender,
    receiver,
    message: {
      messages: message,
    },
    chat_mode: chatMode.toLowerCase(),
    message_type: messageType,
    content_type: contentType,
    file_name: fileName,
    file_type: fileType,
    file_path: filePath,
  };
};
