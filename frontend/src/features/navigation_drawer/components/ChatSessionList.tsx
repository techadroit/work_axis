import { Box, List, Skeleton } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { SessionItem } from './SessionItem.tsx';
import type { ChatSession } from '../../chat/types/chatSession.types';
import { UiEmptyState } from '../../../shared/components/ui';

interface ChatSessionListProps {
  sessions: ChatSession[];
  sessionsLoading: boolean;
  selectedSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
}

/**
 * ChatSessionList Component
 * - Displays the list of chat sessions
 * - Shows loading states and empty states
 */
export const ChatSessionList = ({
  sessions,
  sessionsLoading,
  selectedSessionId,
  onSelectSession,
  onDeleteSession,
}: ChatSessionListProps) => {
  const location = useLocation();
  const isChatRoute = location.pathname.startsWith('/chat');

  return (
    <>
      {/* Sessions List */}
      {sessionsLoading ? (
        <Box sx={{ py: 1 }}>
          {[0, 1, 2].map((item) => (
            <Box key={item} sx={{ px: 1, py: 0.75 }}>
              <Skeleton variant="rounded" height={56} sx={{ borderRadius: '16px' }} />
            </Box>
          ))}
        </Box>
      ) : sessions.length === 0 ? (
        <UiEmptyState
          title="No chat sessions yet"
          description="Start a new chat to create your first conversation thread."
          sx={{ minHeight: 180, mt: 1 }}
        />
      ) : (
        <List disablePadding>
          {sessions.map((session) => (
            <SessionItem
              key={session.chatSessionId}
              session={session}
              isSelected={isChatRoute && selectedSessionId === session.chatSessionId}
              onSelect={onSelectSession}
              onDelete={onDeleteSession}
            />
          ))}
        </List>
      )}
    </>
  );
};

