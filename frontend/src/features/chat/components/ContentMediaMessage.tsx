import {Box, Typography, LinearProgress} from '@mui/material';
import type {ChatMessage} from '../types/chatMessage.types';
import {ContentType} from '../types/chatMessage.types';
import {FileTypeIcon} from './FileTypeIcon';
import { UiChatBubble } from '../../../shared/components/ui';

interface ContentMediaMessageProps {
  message: ChatMessage;
  isCurrentUser: boolean;
  isUploading?: boolean;
  uploadProgress?: number;
}

/**
 * ContentMediaMessage - Renders non-text content like images, files, etc.
 */
export const ContentMediaMessage = ({
  message,
  isCurrentUser,
  isUploading = false,
  uploadProgress = 0,
}: ContentMediaMessageProps) => {
  const contentType = message.message.contentType || ContentType.FILE;
  const metadata = message.message.metadata || {};

  const handleDownload = () => {
    if (metadata.filePath) {
      // In a real app, this would trigger a download
      window.open(metadata.filePath, '_blank');
    }
  };

  const renderImageContent = () => (
    <Box
      sx={{
        maxWidth: '100%',
        borderRadius: 2,
        overflow: 'hidden',
      }}
    >
      <img
        src={metadata.imageUrl || metadata.thumbnailUrl}
        alt={metadata.fileName || 'Image'}
        style={{
          maxWidth: '100%',
          maxHeight: '400px',
          display: 'block',
          objectFit: 'contain',
        }}
      />
      {metadata.fileName && (
        <Box sx={{ p: 1, bgcolor: 'rgba(0, 0, 0, 0.05)' }}>
          <Typography variant="caption" color="text.secondary">
            {metadata.fileName}
          </Typography>
        </Box>
      )}
    </Box>
  );

  const renderFileContent = () => (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 2,
        cursor: metadata.filePath ? 'pointer' : 'default',
        transition: 'opacity 0.2s',
        position: 'relative',
        '&:hover': metadata.filePath
          ? {
              opacity: 0.8,
            }
          : {},
      }}
      onClick={handleDownload}
    >

      {/* Icon container */}
      <Box
        sx={{
          width: 140,
          height: 140,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: 2,
          bgcolor: isCurrentUser ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.03)',
        }}
      >
        <FileTypeIcon
          fileName={metadata.fileName}
          fileType={metadata.fileType}
          size="large"
        />
      </Box>

      {/* File info container */}
      <Box sx={{ width: '100%', textAlign: 'center' }}>
        {/* Upload progress loader */}
        {isUploading && (
          <Box sx={{ mt: 1 }}>
            <LinearProgress
              variant="indeterminate"
              value={uploadProgress}
              sx={{
                height: 4,
                borderRadius: 2,
                bgcolor: 'secondary.main',
                '& .MuiLinearProgress-bar': {
                  bgcolor: 'primary.main',
                },
              }}
            />
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ mt: 0.5, display: 'block' }}
            >
              Uploading...
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );

  return (
    <UiChatBubble
      isCurrentUser={isCurrentUser}
      sx={{
        p: contentType === ContentType.IMAGE ? 0 : 2,
        minWidth: contentType === ContentType.IMAGE ? '200px' : '200px',
        maxWidth: contentType === ContentType.IMAGE ? '400px' : '300px',
        opacity: isUploading ? 0.8 : 1,
      }}
    >
      {contentType === ContentType.IMAGE ? renderImageContent() : renderFileContent()}

      {/* Show message text if present */}
      {message.message.messages && message.message.messages.trim() && (
        <Box sx={{ mt: contentType === ContentType.IMAGE ? 1 : 0, px: contentType === ContentType.IMAGE ? 1.5 : 0, textAlign: 'center' }}>
          <Typography variant="body1">
            {message.message.messages}
          </Typography>
        </Box>
      )}
    </UiChatBubble>
  );
};

