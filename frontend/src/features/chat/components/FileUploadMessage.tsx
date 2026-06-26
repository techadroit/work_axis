import { Box, Paper, Typography, Avatar } from '@mui/material';
import { Image as ImageIcon, Download as DownloadIcon } from '@mui/icons-material';
import { FileTypeIcon } from './FileTypeIcon';

interface FileUploadMessageProps {
  filename: string;
  fileType: string;
  fileUrl?: string;
  isCurrentUser: boolean;
  timestamp: string;
  sender: string;
}

/**
 * FileUploadMessage - Displays a file upload message in chat
 */
export const FileUploadMessage = ({
  filename,
  fileType,
  fileUrl,
  isCurrentUser,
  timestamp,
  sender,
}: FileUploadMessageProps) => {
  const isImage = fileType.startsWith('image/');

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isCurrentUser ? 'flex-end' : 'flex-start',
        alignItems: 'flex-start',
        gap: 1,
      }}
    >
      {/* Avatar for other users (left side) */}
      {!isCurrentUser && (
        <Avatar
          sx={{
            width: 32,
            height: 32,
            bgcolor: 'primary.main',
          }}
        >
          {sender.charAt(0).toUpperCase()}
        </Avatar>
      )}

      {/* Message content */}
      <Box
        sx={{
          maxWidth: '70%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: isCurrentUser ? 'flex-end' : 'flex-start',
        }}
      >
        {/* File preview/icon */}
        <Paper
          elevation={1}
          sx={{
            p: 2,
            bgcolor: isCurrentUser ? 'secondary.main' : 'background.paper',
            color: isCurrentUser ? 'primary.contrastText' : 'text.primary',
            borderRadius: 2,
            minWidth: 200,
            maxWidth: 300,
            position: 'relative',
          }}
        >
          {isImage && fileUrl ? (
            <Box
              component="img"
              src={fileUrl}
              alt={filename}
              sx={{
                maxWidth: '100%',
                maxHeight: 200,
                borderRadius: 1,
                objectFit: 'contain',
              }}
            />
          ) : (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2,
              }}
            >
              {/* Download icon in top-right corner */}
              {fileUrl && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    width: 32,
                    height: 32,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '50%',
                    bgcolor: isCurrentUser ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.05)',
                  }}
                >
                  <DownloadIcon sx={{ fontSize: 18 }} />
                </Box>
              )}

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
                {isImage ? (
                  <ImageIcon sx={{ fontSize: 140, opacity: 0.6 }} />
                ) : (
                  <FileTypeIcon
                    fileName={filename}
                    fileType={fileType}
                    size="large"
                  />
                )}
              </Box>

              {/* File name */}
              <Box sx={{ width: '100%', textAlign: 'center' }}>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 500,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {filename}
                </Typography>
              </Box>
            </Box>
          )}

          {fileUrl && (
            <Typography
              component="a"
              href={fileUrl}
              target="_blank"
              rel="noopener noreferrer"
              variant="caption"
              sx={{
                color: isCurrentUser ? 'primary.contrastText' : 'primary.main',
                textDecoration: 'underline',
                '&:hover': {
                  opacity: 0.8,
                },
              }}
            >
              📎 {isImage ? 'View full image' : 'Download file'}
            </Typography>
          )}
        </Paper>

        {/* Timestamp */}
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ mt: 0.5, px: 1 }}
        >
          {new Date(timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Typography>
      </Box>

      {/* Avatar for current user (right side) */}
      {isCurrentUser && (
        <Avatar
          sx={{
            width: 32,
            height: 32,
            bgcolor: 'secondary.main',
          }}
        >
          {sender.charAt(0).toUpperCase()}
        </Avatar>
      )}
    </Box>
  );
};

