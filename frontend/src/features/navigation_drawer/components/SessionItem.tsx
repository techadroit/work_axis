import { Box, ListItem, ListItemButton, ListItemText, Typography } from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import type { ChatSession } from '../../chat/types/chatSession.types';
import { getNavigationItemStyles } from '../../../design_system/styles/navigation_styles/navigationStyles.ts';
import { UiIconButton } from '../../../shared/components/ui';

const SESSION_COLORS = ['#0EA5A4', '#F2B43C', '#3B82F6', '#7C3AED', '#059669', '#EF4444'];
const getSessionColor = (id: string) =>
  SESSION_COLORS[id.charCodeAt(0) % SESSION_COLORS.length];

interface SessionItemProps {
  session: ChatSession;
  isSelected: boolean;
  onSelect: (sessionId: string) => void;
  onDelete: (sessionId: string) => void;
}

/**
 * SessionItem - Displays a chat session with title and delete option
 */
export const SessionItem = ({ session, isSelected, onSelect, onDelete }: SessionItemProps) => {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the select action
    onDelete(session.chatSessionId);
  };

  return (
    <ListItem
      disablePadding
      secondaryAction={
        <UiIconButton
          edge="end"
          aria-label="delete"
          onClick={handleDelete}
          size="small"
          tone="ghost"
          sx={{ width: 32, height: 32 }}
        >
          <DeleteIcon fontSize="small" />
        </UiIconButton>
      }
    >
      <ListItemButton
        selected={isSelected}
        onClick={() => onSelect(session.chatSessionId)}
        sx={{ ...getNavigationItemStyles(), gap: 1 }}
      >
        <Box
          sx={{
            width: 30,
            height: 30,
            borderRadius: '50%',
            backgroundColor: getSessionColor(session.chatSessionId),
            display: 'grid',
            placeItems: 'center',
            flexShrink: 0,
            opacity: 0.88,
          }}
        >
          <Typography sx={{ fontSize: '0.68rem', fontWeight: 700, color: '#fff', lineHeight: 1 }}>
            {(session.title || 'U').charAt(0).toUpperCase()}
          </Typography>
        </Box>
        <ListItemText
          primary={session.title || 'Untitled Chat'}
          secondary={new Date(session.createdAt).toLocaleDateString()}
          slotProps={{
            primary: { noWrap: true, sx: { pr: 2, fontSize: '0.82rem', fontWeight: 600 } },
            secondary: { sx: { fontSize: '0.7rem' } },
          }}
        />
      </ListItemButton>
    </ListItem>
  );
};

