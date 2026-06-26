import { Typography } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ChatMessage } from '../types/chatMessage.types';
import { UiChatBubble } from '../../../shared/components/ui';

interface ContentTextMessageProps {
  message: ChatMessage;
  isCurrentUser: boolean;
  isStreaming?: boolean;
}

/**
 * ContentTextMessage - Renders the text content of a chat message with markdown support
 */
export const ContentTextMessage = ({
  message,
  isCurrentUser,
}: ContentTextMessageProps) => {
  return (
    <UiChatBubble
      isCurrentUser={isCurrentUser}
      sx={{
        p: 1.5,
        wordBreak: 'break-word',
        '& p': {
          margin: 0,
          marginBottom: '0.5em',
          '&:last-child': {
            marginBottom: 0,
          },
        },
        '& ul, & ol': {
          margin: 0,
          paddingLeft: '1.5em',
          marginBottom: '0.5em',
          '&:last-child': {
            marginBottom: 0,
          },
        },
        '& li': {
          marginBottom: '0.25em',
        },
        '& code': {
          bgcolor: isCurrentUser ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.05)',
          padding: '0.2em 0.4em',
          borderRadius: '3px',
          fontSize: '0.9em',
        },
        '& pre': {
          bgcolor: isCurrentUser ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.05)',
          padding: '0.75em',
          borderRadius: '4px',
          overflow: 'auto',
          margin: '0.5em 0',
          '&:last-child': {
            marginBottom: 0,
          },
        },
        '& pre code': {
          bgcolor: 'transparent',
          padding: 0,
        },
        '& blockquote': {
          borderLeft: isCurrentUser
            ? '3px solid rgba(255, 255, 255, 0.5)'
            : '3px solid rgba(0, 0, 0, 0.2)',
          margin: '0.5em 0',
          paddingLeft: '1em',
          '&:last-child': {
            marginBottom: 0,
          },
        },
        '& h1, & h2, & h3, & h4, & h5, & h6': {
          margin: '0.5em 0 0.3em 0',
          '&:first-of-type': {
            marginTop: 0,
          },
          '&:last-child': {
            marginBottom: 0,
          },
        },
        '& a': {
          color: isCurrentUser ? 'inherit' : 'primary.main',
          textDecoration: 'underline',
        },
        '& table': {
          borderCollapse: 'collapse',
          width: '100%',
          margin: '0.5em 0',
          '&:last-child': {
            marginBottom: 0,
          },
        },
        '& th, & td': {
          border: isCurrentUser
            ? '1px solid rgba(255, 255, 255, 0.3)'
            : '1px solid rgba(0, 0, 0, 0.1)',
          padding: '0.5em',
          textAlign: 'left',
        },
        '& th': {
          bgcolor: isCurrentUser ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.03)',
          fontWeight: 'bold',
        },
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => (
            <Typography variant="body1" component="span" sx={{ display: 'block' }}>
              {children}
            </Typography>
          ),
        }}
      >
        {message.message.messages}
      </ReactMarkdown>
    </UiChatBubble>
  );
};

