import { Box, Alert } from '@mui/material';
import { useEffect, useRef, useState, useMemo } from 'react';
import { useParams, useNavigate, useOutletContext, useLocation } from 'react-router-dom';
import { Menu as MenuIcon } from '@mui/icons-material';
import { ChatBody } from './ChatBody';
import { ChatFooter } from './ChatFooter';
import { useChatDispatch, useChatSelector } from '../stores/chatStore';
import { loadMessages, addMessageOptimistically, setTyping } from '../stores/chatSlice';
import { startFileUpload, updateFileUploadProgress, completeFileUpload } from '../stores/fileUploadSlice';
import { useUserSelector } from '../../../shared/stores/userStore';
import { useChatSessionDispatch, useChatSessionSelector } from '../../../shared/stores/chatSessionStore';
import { createChatSession } from '../../../shared/hooks/useCreateChatSession';
import { loadChatSessions } from '../../../shared/hooks/useLoadChatSessions';
import { selectSession } from '../../../shared/stores/chatSessionSlice';
import { logger } from '../../../core/logger';
import { messageService } from '../../../data/services';
import { createWebSocketMessage } from '../utils/messageHelpers';
import { ChatModeType, ContentType, type ChatMessage } from '../types/chatMessage.types';
import { useChatMessageListener } from '../hooks/useChatMessageListener';
import { fileUploadService } from '../services/FileUploadService';
import type { FileData } from '../types/fileUpload.types';
import { utcNowIso } from '../../../util/TimeUtil';
import { UiMessageSkeleton, UiSectionTitle, UiIconButton } from '../../../shared/components/ui';

/**
 * ChatInterface - Main chat component that displays messages and handles sending
 */
export const ChatInterface = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const location = useLocation();
  const initialChatMode = (location.state as { chatMode?: ChatModeType } | null)?.chatMode ?? ChatModeType.CHAT;
  const [pageSize] = useState(20);

  // Outlet context provided by MainScreen — used to embed drawer toggle in this header
  const { toggleDrawer, isConnected, isLargeScreen, connectionLabel } =
    useOutletContext<{ toggleDrawer: () => void; isConnected: boolean; isLargeScreen: boolean; connectionLabel: string }>();

  const navigate = useNavigate();
  const chatDispatch = useChatDispatch();
  const chatSessionDispatch = useChatSessionDispatch();

  // Store actual File objects in a ref (not in Redux)
  const fileObjectsRef = useRef<Map<string, File>>(new Map());

  // Ref for the scrollable container to detect scroll events
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const isLoadingMoreRef = useRef(false);

  // Ref for typing timeout
  const typingTimeoutRef = useRef<number | null>(null);

  // Listen for chat messages (MessageType.MESSAGE)
  useChatMessageListener();

  // Get current user
  const { userId } = useUserSelector(state => state.user);

  // Get chat session details
  const sessions = useChatSessionSelector(state => state.chatSession.sessions);
  const currentSession = sessions.find(s => s.chatSessionId === sessionId);

  // Get messages for this session
  // (effectiveMessages below is used to support draft chats)

  const loading = useChatSelector(state => state.chat.loading);
  const loadingMore = useChatSelector(state => state.chat.loadingMore);
  const sendingMessage = useChatSelector(state => state.chat.sendingMessage);
  const error = useChatSelector(state => state.chat.error);
  const isTyping = useChatSelector(state => state.chat.isTyping);

  // Get pagination info
  const paginationInfo = useChatSelector(state =>
    sessionId ? state.chat.paginationByChatSession[sessionId] : undefined
  );

  // Get file upload state
  const uploadingFiles = useChatSelector(state => state.fileUpload.uploadingFiles);

  // Load messages when session changes
  useEffect(() => {
    if (sessionId) {
      logger.info('Loading chat interface', { sessionId, pageNo: 0, pageSize });
      chatDispatch(loadMessages({ sessionId, pageNo: 0, pageSize }));

      // Clear typing indicator and timeout when switching sessions
      chatDispatch(setTyping(false));
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
        typingTimeoutRef.current = null;
      }
    }
  }, [sessionId, pageSize, chatDispatch]);

  // Cleanup typing timeout on unmount
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  // Handle scroll events to detect when user scrolls to top for pagination
  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;
    if (!scrollContainer) return;

    const handleScroll = () => {
      const { scrollTop } = scrollContainer;
      const thresholdPx = 100; // Trigger when within 100px of top

      // Check if user scrolled near top
      if (scrollTop <= thresholdPx && paginationInfo?.hasNext && !loadingMore && !isLoadingMoreRef.current) {
        logger.info('Near top, loading more messages', { scrollTop, hasNext: paginationInfo.hasNext });
        isLoadingMoreRef.current = true;
        handleLoadMore();
      }
    };

    scrollContainer.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      scrollContainer.removeEventListener('scroll', handleScroll);
    };
  }, [paginationInfo?.hasNext, loadingMore]);

  // Reset loading flag when loadingMore changes
  useEffect(() => {
    if (!loadingMore) {
      isLoadingMoreRef.current = false;
    }
  }, [loadingMore]);

  const ensureSession = async (): Promise<string | null> => {
    if (sessionId) return sessionId;
    if (!userId) return null;

    const resultAction = await chatSessionDispatch(createChatSession({
      userId,
      title: 'New Chat',
    }));

    if (!createChatSession.fulfilled.match(resultAction)) {
      logger.error('Failed to create session for draft chat', resultAction);
      return null;
    }

    const newSessionId = resultAction.payload;

    // Refresh drawer sessions
    await chatSessionDispatch(loadChatSessions(userId));
    chatSessionDispatch(selectSession(newSessionId));

    // Replace URL so the current screen becomes the real session screen
    navigate(`/chat/${newSessionId}`, { replace: true });

    return newSessionId;
  };

  const handleLoadMore = async () => {
    if (!sessionId || !paginationInfo) return;

    // Check if there are more pages to load
    if (!paginationInfo.hasNext || loadingMore) return;

    const nextPage = paginationInfo.currentPage + 1;
    logger.info('Loading more messages', { sessionId, nextPage, pageSize });

    await chatDispatch(loadMessages({ sessionId, pageNo: nextPage, pageSize }));
  };

  const handleSendMessage = async (message: string, chatMode: ChatModeType = ChatModeType.AGENT) => {
    if (!userId) {
      logger.error('Cannot send message: missing userId');
      return;
    }

    if (!messageService.isConnected()) {
      logger.error('Cannot send message: WebSocket is not connected');
      return;
    }

    const actualSessionId = await ensureSession();
    if (!actualSessionId) {
      logger.error('Cannot send message: missing sessionId');
      return;
    }

    try {
      // Show typing indicator
      chatDispatch(setTyping(true));

      // Clear any existing timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }

      // Set 30-second timeout to clear typing indicator
      typingTimeoutRef.current = setTimeout(() => {
        logger.warn('Message send timeout reached (30 seconds)');
        chatDispatch(setTyping(false));
      }, 60000);

      // Create WebSocket message payload
      const wsMessage = createWebSocketMessage({
        sessionId: actualSessionId,
        message,
        sender: userId,
        receiver: 'assistant',
        chatMode: chatMode,
      });

      logger.info('Sending message via WebSocket', {
        messageId: wsMessage.message_id,
        sessionId: actualSessionId,
        chatMode
      });

      // Optimistically add the message to the UI
      const optimisticMessage: ChatMessage = {
        messageId: wsMessage.message_id,
        chatSessionId: wsMessage.chat_session_id,
        utcTime: wsMessage.utc_time,
        sender: wsMessage.sender,
        receiver: wsMessage.receiver,
        message: wsMessage.message,
        chatMode: chatMode,
        contentType: wsMessage.content_type as any,
        mimeType: wsMessage.file_type || '',
        filePath: wsMessage.file_path || '',
        fileName: wsMessage.file_name || '',
      };

      chatDispatch(addMessageOptimistically({
        sessionId: actualSessionId,
        message: optimisticMessage,
      }));

      // Send through WebSocket
      messageService.sendMessage(wsMessage);

      logger.info('Message sent successfully via WebSocket');
    } catch (error) {
      logger.error('Failed to send message via WebSocket', error);
      // Clear typing indicator on error
      chatDispatch(setTyping(false));
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    }
  };

  const handleFileSelect = (filesWithMetadata: Array<FileData & { file?: File }>) => {
    filesWithMetadata.forEach(async (fileData) => {
      // Generate unique file ID
      const fileId = `${fileData.name}_${Date.now()}`;

      // Extract only serializable data for Redux
      const serializableFileData: FileData = {
        name: fileData.name,
        size: fileData.size,
        type: fileData.type,
        lastModified: fileData.lastModified,
        preview: fileData.preview,
      };

      // Add to uploading files with fileId
      chatDispatch(startFileUpload({ ...serializableFileData, fileId }));

      // Store actual File object in ref if it exists
      if (fileData.file instanceof File) {
        const fileKey = `${fileData.name}_${fileData.lastModified}`;
        fileObjectsRef.current.set(fileKey, fileData.file);

        // Ensure session exists, then auto-upload
        const actualSessionId = await ensureSession();
        if (actualSessionId && userId) {
          handleFileUpload(actualSessionId, fileData.file, serializableFileData, fileId);
        }
      }
    });
  };

  const handleFileUpload = async (actualSessionId: string, file: File, fileData: FileData, fileId: string) => {
    if (!actualSessionId || !userId) {
      logger.error('Cannot upload file: missing sessionId or userId');
      return;
    }

    try {
      const response = await fileUploadService.uploadFile(
        file,
        actualSessionId,
        userId,
        (progress) => {
          // Update upload progress
          chatDispatch(updateFileUploadProgress({ fileId, progress }));
        }
      );

      logger.info('File uploaded successfully', response);

      // Remove from uploading files
      chatDispatch(completeFileUpload(fileId));

      // Create a message indicating file upload
      const fileMessage: ChatMessage = {
        messageId: Date.now().toString(),
        chatSessionId: actualSessionId,
        utcTime: utcNowIso(),
        sender: userId,
        receiver: 'assistant',
        message: {
          messages: '', // keep empty; UI already shows fileName
          contentType: ContentType.FILE,
          metadata: {
            fileName: fileData.name,
            fileSize: fileData.size,
            fileType: fileData.type,
            filePath: response.file_path,
          },
        },
        chatMode: ChatModeType.AGENT,
        contentType: ContentType.FILE,
        mimeType: fileData.type,
        filePath: response.file_path,
        fileName: fileData.name,
      };

      // Add file upload message to chat
      chatDispatch(addMessageOptimistically({
        sessionId: actualSessionId,
        message: fileMessage,
      }));

    } catch (error) {
      logger.error('File upload failed', error);
      // Remove from uploading files on error
      chatDispatch(completeFileUpload(fileId));
    }
  };

  const effectiveSessionId = sessionId || '';

  // Get completed messages
  const completedMessages = useChatSelector(
    state => state.chat.messagesByChatSession[effectiveSessionId] || []
  );

  // Get streaming messages
  const streamingMessages = useChatSelector(
    state => state.chat.streamingMessagesByChatSession[effectiveSessionId] || []
  );

  // Combine completed and streaming messages for display
  // Use useMemo to ensure proper re-rendering when streaming messages update
  const effectiveMessages = useMemo(() => {
    const combined = [...completedMessages, ...streamingMessages];

    // Sort by timestamp to maintain chronological order
    // This ensures messages appear in the correct order even when streaming messages
    // are moved from streaming to completed state
    combined.sort((a, b) => {
      const timeA = new Date(a.utcTime).getTime();
      const timeB = new Date(b.utcTime).getTime();
      return timeA - timeB; // Oldest first
    });

    console.log('[CHAT INTERFACE] Messages updated:', {
      sessionId: effectiveSessionId,
      completedCount: completedMessages.length,
      streamingCount: streamingMessages.length,
      totalCount: combined.length,
      streamingMessages: streamingMessages.map(m => ({
        id: m.messageId,
        contentLength: m.message.messages.length,
      })),
    });
    return combined;
  }, [completedMessages, streamingMessages, effectiveSessionId]);

  // Extract streaming message IDs for the ChatBody component
  const streamingMessageIds = useMemo(() => {
    return streamingMessages.map(m => m.messageId);
  }, [streamingMessages]);

  // Draft chat (no sessionId): show empty conversation + footer.

  if (loading && sessionId && effectiveMessages.length === 0) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          gap: 2,
          height: '100%',
          px: { xs: 2, md: 4 },
          py: 3,
        }}
      >
        <UiMessageSkeleton align="left" />
        <UiMessageSkeleton align="right" />
        <UiMessageSkeleton align="left" />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        bgcolor: 'transparent',
      }}
    >
      {/* Chat Header */}
      <Box
        sx={{
          px: { xs: 1.5, md: 3 },
          py: { xs: 1, md: 2 },
          borderBottom: '1px solid var(--border-subtle)',
          backgroundColor: 'color-mix(in srgb, var(--surface-primary) 78%, transparent)',
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        {/* Hamburger — only on small screens where the drawer is not permanently visible */}
        {!isLargeScreen && (
          <UiIconButton
            tone="ghost"
            size="small"
            aria-label="open navigation"
            onClick={toggleDrawer}
            sx={{ flexShrink: 0 }}
          >
            <MenuIcon />
          </UiIconButton>
        )}

        {/* Title — takes remaining space */}
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <UiSectionTitle eyebrow={sessionId ? 'Active Conversation' : 'Draft Chat'}>
            {sessionId ? (currentSession?.title || 'Chat') : 'New Chat'}
          </UiSectionTitle>
        </Box>

        {/* Connection badge — only on small screens */}
        {!isLargeScreen && (
          <Box
            sx={{
              px: 1.25,
              py: 0.6,
              borderRadius: '999px',
              border: '1px solid var(--border-subtle)',
              backgroundColor: 'color-mix(in srgb, var(--surface-secondary) 85%, transparent)',
              display: 'flex',
              alignItems: 'center',
              gap: 0.75,
              flexShrink: 0,
            }}
          >
            <Box
              sx={{
                width: 7,
                height: 7,
                borderRadius: '50%',
                backgroundColor: isConnected ? 'success.main' : 'warning.main',
              }}
            />
            <Box
              component="span"
              sx={{ fontSize: '11px', fontWeight: 700, color: 'text.secondary', lineHeight: 1 }}
            >
              {connectionLabel}
            </Box>
          </Box>
        )}
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" onClose={() => {}} sx={{ m: 2, flexShrink: 0 }}>
          {error}
        </Alert>
      )}

      {/* Chat Body */}
      <Box
        ref={scrollContainerRef}
        sx={{
          flex: 1,
          overflow: 'auto',
          minHeight: 0,
          bgcolor: 'transparent',
        }}
      >
        <ChatBody
          sessionId={effectiveSessionId}
          messages={sessionId ? effectiveMessages : []}
          currentUserId={userId || ''}
          streamingMessageIds={streamingMessageIds}
          uploadingFiles={uploadingFiles}
          hasMoreMessages={paginationInfo?.hasNext || false}
          loadingMore={loadingMore}
          onLoadMore={handleLoadMore}
          scrollContainerRef={scrollContainerRef}
          isTyping={isTyping}
        />
      </Box>

      {/* Chat Footer */}
      <Box
        sx={{
          flexShrink: 0,
          borderTop: '1px solid var(--border-subtle)',
          bgcolor: 'color-mix(in srgb, var(--surface-primary) 82%, transparent)',
        }}
      >
        <ChatFooter
          onSendMessage={handleSendMessage}
          disabled={!userId || isTyping}
          sending={sendingMessage || isTyping}
          chatMode={initialChatMode}
          onFileSelect={handleFileSelect}
        />
      </Box>
    </Box>
  );
};

