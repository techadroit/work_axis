import { Box } from '@mui/material';
import { UiChatBubble, UiLoadingDots, UiParticipantAvatar } from '../../../shared/components/ui';

interface TypingIndicatorProps {
  isCurrentUser?: boolean;
}

/**
 * TypingIndicator - Shows a bouncing dots animation to indicate typing
 */
export const TypingIndicator = ({ isCurrentUser = false }: TypingIndicatorProps) => {
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
      <Box
        sx={{
          maxWidth: '70%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: isCurrentUser ? 'flex-end' : 'flex-start',
        }}
      >
        <UiChatBubble isCurrentUser={isCurrentUser} sx={{ px: 2, py: 1.5, minWidth: 68 }}>
          <UiLoadingDots isCurrentUser={isCurrentUser} />
        </UiChatBubble>
      </Box>
      {isCurrentUser && <UiParticipantAvatar isCurrentUser />}
    </Box>
  );
};

