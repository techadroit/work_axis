import {Box, Typography} from '@mui/material';
import type {ChatMessage} from '../types/chatMessage.types';
import {ContentType} from '../types/chatMessage.types';
import {ContentTextMessage} from './ContentTextMessage';
import {ContentMediaMessage} from './ContentMediaMessage';
import { UiParticipantAvatar } from '../../../shared/components/ui';

interface MessageBodyProps {
    message: ChatMessage;
    isCurrentUser: boolean;
    isStreaming?: boolean;
}

const formatUtcTimeToLocalHHmm = (utcTime: unknown): string => {
    if (typeof utcTime !== 'string' || utcTime.trim().length === 0) return '';

    // Normalize common non-ISO variants (defensive)
    const normalized = utcTime.includes(' ') && !utcTime.includes('T')
        ? utcTime.replace(' ', 'T')
        : utcTime;

    const date = new Date(normalized);
    if (Number.isNaN(date.getTime())) return '';

    return new Intl.DateTimeFormat(undefined, {
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
};

/**
 * MessageBody - Displays a single chat message with avatar and timestamp
 */
export const MessageBody = ({message, isCurrentUser, isStreaming = false}: MessageBodyProps) => {
    const timeLabel = formatUtcTimeToLocalHHmm(message.utcTime);
    return (
        <Box
            sx={{
                display: 'flex',
                justifyContent: isCurrentUser ? 'flex-end' : 'flex-start',
                alignItems: 'flex-start',
                gap: 1,
            }}
        >
            {!isCurrentUser && <UiParticipantAvatar isCurrentUser={false} />}

            {/* Message content */}
            <Box
                sx={{
                    maxWidth: { xs: '82%', md: '70%' },
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: isCurrentUser ? 'flex-end' : 'flex-start',
                }}
            >
                {/* Message bubble */}
                {message.contentType === ContentType.TEXT ? (
                    <ContentTextMessage
                        message={message}
                        isCurrentUser={isCurrentUser}
                        isStreaming={isStreaming}
                    />
                ) : (
                    <ContentMediaMessage
                        message={message}
                        isCurrentUser={isCurrentUser}
                    />
                )}

                {/* Timestamp */}
                <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{mt: 0.5, px: 1}}
                >
                    {timeLabel}
                </Typography>
            </Box>

            {isCurrentUser && <UiParticipantAvatar isCurrentUser />}
        </Box>
    );
};

