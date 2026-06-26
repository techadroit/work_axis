import type {WebSocketMessage} from "../utils/messageHelpers.ts";
import { parseUtcIso } from '../../../util/TimeUtil';

export interface MessageResponse {
    message_id: string;
    chat_session_id: string;
    utc_time: string;
    sender: string;
    receiver: string;
    messages: string;
    mode?: string; // Optional: may be missing in streaming messages
    created_at?: string;
    mime_type: string;
    file_path: string;
    file_name: string;
    content_type: string;
}

export interface PaginatedChatResponse {
    messages: MessageResponse[];
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
}

export enum ChatModeType {
    AGENT = 'agent',
    CHAT = 'offline',
    OFFLINE = 'offline', // kept for backward-compat; UI uses CHAT instead
}

const toContentType = (contentType: string): ContentType => {
    const normalizedType = contentType?.toLowerCase();

    switch (normalizedType) {
        case 'image':
            return ContentType.IMAGE;
        case 'file':
            return ContentType.FILE;
        case 'text':
        default:
            return ContentType.TEXT;
    }
};

export enum MessageType {
    MESSAGE = 'message',
    UPDATE_TITLE = 'update_title',
}

export enum ContentType {
    TEXT = 'text',
    IMAGE = 'image',
    FILE = 'file',
}

export interface ChatMessageBody {
    messages: string;
    contentType?: ContentType;
    metadata?: {
        fileName?: string;
        fileSize?: number;
        fileType?: string;
        filePath?: string;
        imageUrl?: string;
        thumbnailUrl?: string;
    };
}

export interface ChatMessage {
    messageId: string;
    chatSessionId: string;
    utcTime: string;
    sender: string;
    receiver: string;
    message: ChatMessageBody;
    chatMode: ChatModeType;
    contentType?: ContentType;
    mimeType: string;
    filePath: string;
    fileName: string;
}

// Mapper function for API responses
export const toChatMessage = (response: MessageResponse): ChatMessage => {
    const contentType = toContentType(response.content_type);

    return {
        messageId: response.message_id,
        chatSessionId: response.chat_session_id,
        utcTime: parseUtcIso(response.utc_time).toISOString(),
        sender: response.sender,
        receiver: response.receiver,
        message: {
            messages: response.messages,
            contentType: contentType,
            metadata: contentType !== ContentType.TEXT ? {
                fileName: response.file_name || undefined,
                fileType: response.mime_type || undefined,
                filePath: response.file_path || undefined,
            } : undefined,
        },
        chatMode: (response.mode?.toUpperCase() || ChatModeType.AGENT) as ChatModeType,
        contentType: contentType,
        mimeType: response.mime_type || '',
        filePath: response.file_path || '',
        fileName: response.file_name || '',
    };
};

// Mapper function for WebSocket messages
export const toChatMessageFromWebsocket = (response: WebSocketMessage): ChatMessage => {
    const contentType = toContentType(response.content_type);

    return {
        messageId: response.message_id,
        chatSessionId: response.chat_session_id,
        utcTime: parseUtcIso(response.utc_time).toISOString(),
        sender: response.sender,
        receiver: response.receiver,
        message: {
            messages: response.message.messages
        },
        chatMode: (response.chat_mode?.toUpperCase() || ChatModeType.AGENT) as ChatModeType,
        contentType: contentType,
        mimeType: response.file_type || '',
        filePath: response.file_path || '',
        fileName: response.file_name || '',
    };
};
