import { Box, CircularProgress } from '@mui/material';
import { useRef, useEffect } from 'react';
import type { ChatMessage } from '../types/chatMessage.types';
import type { FileData } from '../types/fileUpload.types';
import { MessageBody } from './MessageBody';
import { ContentMediaMessage } from './ContentMediaMessage';
import { ContentType } from '../types/chatMessage.types';
import { utcNowIso } from '../../../util/TimeUtil';
import { TypingIndicator } from './TypingIndicator';
import { AutoAwesomeOutlined } from '@mui/icons-material';
import { UiEmptyState } from '../../../shared/components/ui';

interface ChatBodyProps {
  sessionId: string;
  messages: ChatMessage[];
  currentUserId: string;
  streamingMessageIds?: string[];
  uploadingFiles?: Array<FileData & { fileId: string; uploadProgress: number }>;
  hasMoreMessages?: boolean;
  loadingMore?: boolean;
  onLoadMore?: () => void;
  scrollContainerRef?: React.RefObject<HTMLDivElement>;
  isTyping?: boolean;
}

/**
 * ChatBody - Displays the list of chat messages
 */
export const ChatBody = ({
  sessionId,
  messages,
  currentUserId,
  streamingMessageIds = [],
  uploadingFiles = [],
  hasMoreMessages: _hasMoreMessages = false,
  loadingMore = false,
  onLoadMore: _onLoadMore,
  scrollContainerRef: parentScrollRef,
  isTyping = false,
}: ChatBodyProps) => {
  const contentContainerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const shouldStickToBottomRef = useRef(true);
  const isInitialScrollDoneRef = useRef(false);

  // Debug logging to verify messages are received
  useEffect(() => {
    console.log('[CHAT BODY] Rendering messages:', {
      sessionId,
      messageCount: messages.length,
      streamingMessageIds,
      messages: messages.map(m => ({
        id: m.messageId,
        sender: m.sender,
        contentLength: m.message.messages.length,
        preview: m.message.messages.substring(0, 30),
      })),
    });
  }, [sessionId, messages, streamingMessageIds]);

  const isNearBottom = () => {
    // Use parent scroll container if provided, otherwise use content container
    const el = parentScrollRef?.current || contentContainerRef.current;
    if (!el) return true;

    // How close (px) to the bottom we still consider "at bottom"
    const thresholdPx = 120;
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    return distanceFromBottom <= thresholdPx;
  };

  const scrollToBottom = (behavior: ScrollBehavior) => {
    messagesEndRef.current?.scrollIntoView({ behavior, block: 'end' });
  };

  // Track whether the user is at/near bottom
  useEffect(() => {
    const el = parentScrollRef?.current || contentContainerRef.current;
    if (!el) return;

    const onScroll = () => {
      shouldStickToBottomRef.current = isNearBottom();
    };

    el.addEventListener('scroll', onScroll, { passive: true });
    // Initialize stickiness based on current position
    shouldStickToBottomRef.current = isNearBottom();

    return () => {
      el.removeEventListener('scroll', onScroll);
    };
  }, [parentScrollRef]);

  // Initial: snap to bottom (no animation) so the latest message is visible immediately.
  useEffect(() => {
    if (isInitialScrollDoneRef.current) return;

    // Wait one tick so layout/measurements are correct.
    const id = window.requestAnimationFrame(() => {
      scrollToBottom('auto');
      isInitialScrollDoneRef.current = true;
    });

    return () => window.cancelAnimationFrame(id);
    // Only once on mount.
  }, []);

  // When switching sessions, always snap to bottom (no animation) for the newly selected session.
  useEffect(() => {
    // New session starts in "stick to bottom" mode.
    shouldStickToBottomRef.current = true;

    // We want an immediate jump but only after the new session's messages render.
    isInitialScrollDoneRef.current = false;

    const id = window.requestAnimationFrame(() => {
      scrollToBottom('auto');
      isInitialScrollDoneRef.current = true;
    });

    return () => window.cancelAnimationFrame(id);
  }, [sessionId]);

  // If messages are empty (common during session switch/loading), allow a fresh initial snap
  // once messages arrive, instead of doing a smooth scroll.
  useEffect(() => {
    if (messages.length === 0 && uploadingFiles.length === 0 && !isTyping) {
      isInitialScrollDoneRef.current = false;
      shouldStickToBottomRef.current = true;
    }
  }, [messages.length, uploadingFiles.length, isTyping]);

  // Subsequent updates: only auto-scroll if the user is already at the bottom.
  useEffect(() => {
    if (!isInitialScrollDoneRef.current) {
      // First paint after a reset: snap (no animation) so we never see a scroll animation.
      scrollToBottom('auto');
      isInitialScrollDoneRef.current = true;
      return;
    }
    if (!shouldStickToBottomRef.current) return;

    scrollToBottom('smooth');
  }, [messages, uploadingFiles, isTyping]);

  return (
    <Box
      ref={contentContainerRef}
      sx={{
        minHeight: '100%',
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
      }}
    >
      {messages.length === 0 && uploadingFiles.length === 0 && !isTyping ? (
        <UiEmptyState
          title="Start a new conversation"
          description="Ask a question, attach a file, or switch modes to begin the thread."
          icon={<AutoAwesomeOutlined />}
          sx={{ height: '100%' }}
        />
      ) : (
        <>
          {/* Loading indicator at the top when loading more */}
          {loadingMore && (
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                py: 2,
              }}
            >
              <CircularProgress size={24} />
            </Box>
          )}

          {messages.map((message) => {
            const isCurrentUser = message.sender === currentUserId;
            const isStreaming = streamingMessageIds.includes(message.messageId);

            return (
              <MessageBody
                key={message.messageId}
                message={message}
                isCurrentUser={isCurrentUser}
                isStreaming={isStreaming}
              />
            );
          })}

          {/* Show uploading files */}
          {uploadingFiles.map((file) => {
            // Create a temporary ChatMessage object for uploading files
            const tempMessage: ChatMessage = {
              messageId: file.fileId,
              sender: currentUserId,
              receiver: '',
              chatSessionId: '',
              utcTime: utcNowIso(),
              chatMode: 'NORMAL' as any,
              mimeType: file.type,
              filePath: '',
              fileName: file.name,
              message: {
                contentType: file.type.startsWith('image/') ? ContentType.IMAGE : ContentType.FILE,
                messages: '',
                metadata: {
                  fileName: file.name,
                  fileType: file.type,
                  fileSize: file.size,
                  imageUrl: file.preview,
                },
              },
            };

            return (
              <Box
                key={file.fileId}
                sx={{
                  display: 'flex',
                  justifyContent: 'flex-end',
                  alignItems: 'flex-start',
                }}
              >
                <ContentMediaMessage
                  message={tempMessage}
                  isCurrentUser={true}
                  isUploading={true}
                  uploadProgress={file.uploadProgress}
                />
              </Box>
            );
          })}

          {/* Show typing indicator */}
          {isTyping && <TypingIndicator isCurrentUser={false} />}

          <div ref={messagesEndRef} />
        </>
      )}
    </Box>
  );
};
