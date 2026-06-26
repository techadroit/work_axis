import { Box, Typography, List, ListItem, ListItemText, CircularProgress, Alert } from '@mui/material';
import { useChatSessionSelector } from '../../../shared/stores/chatSessionStore';

/**
 * Example component showing how to use ChatSessionStore
 */
export const ChatSessionList = () => {
  const { sessions, loading, error } = useChatSessionSelector(state => state.chatSession);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Error loading chat sessions: {error}</Alert>
      </Box>
    );
  }

  if (sessions.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="text.secondary">No chat sessions found</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Chat Sessions ({sessions.length})
      </Typography>
      <List>
        {sessions.map(session => (
          <ListItem key={session.chatSessionId}>
            <ListItemText
              primary={session.title || 'Untitled Session'}
              secondary={`Created: ${new Date(session.createdAt).toLocaleString()}`}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

