import { Box, Paper, Typography, LinearProgress } from '@mui/material';
import {
  Image as ImageIcon,
} from '@mui/icons-material';
import type { FileData } from '../types/fileUpload.types';
import { FileTypeIcon } from './FileTypeIcon';

interface FileUploadingMessageProps {
  file: FileData;
  isCurrentUser: boolean;
  uploadProgress?: number;
}

/**
 * FileUploadingMessage - Shows a file being uploaded with a progress loader
 */
export const FileUploadingMessage = ({
  file,
  isCurrentUser,
  uploadProgress = 0,
}: FileUploadingMessageProps) => {
  const isImage = file.type.startsWith('image/');

  // const formatFileSize = (bytes: number): string => {
  //   if (bytes < 1024) return `${bytes} B`;
  //   if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  //   return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  // };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isCurrentUser ? 'flex-end' : 'flex-start',
        alignItems: 'flex-start',
        gap: 1,
      }}
    >
      {/* Message content */}
      <Box
        sx={{
          maxWidth: '70%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: isCurrentUser ? 'flex-end' : 'flex-start',
        }}
      >
        <Paper
          elevation={1}
          sx={{
            p: 2,
            bgcolor: isCurrentUser ? 'secondary.main' : 'background.paper',
            color: isCurrentUser ? 'primary.contrastText' : 'text.primary',
            borderRadius: 2,
            minWidth: 200,
            maxWidth: 300,
            opacity: 0.8,
          }}
        >
          {/* Image preview if available */}
          {isImage && file.preview && (
            <Box
              sx={{
                mb: 2,
                borderRadius: 1,
                overflow: 'hidden',
              }}
            >
              <img
                src={file.preview}
                alt={file.name}
                style={{
                  maxWidth: '100%',
                  maxHeight: 200,
                  display: 'block',
                  objectFit: 'contain',
                }}
              />
            </Box>
          )}

          {/* File info - vertical layout */}
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
            }}
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
              {isImage ? (
                <ImageIcon sx={{ fontSize: 140, opacity: 0.6 }} />
              ) : (
                <FileTypeIcon
                  fileName={file.name}
                  fileType={file.type}
                  size="large"
                />
              )}
            </Box>

            {/* File name and size */}
            <Box sx={{ width: '100%', textAlign: 'center' }}>
              <Typography
                variant="body2"
                sx={{
                  fontWeight: 500,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  mb: 0.5,
                }}
              >
                {file.name}
              </Typography>
              {/*<Typography variant="caption" color="text.secondary">*/}
              {/*  {formatFileSize(file.size)}*/}
              {/*</Typography>*/}
            </Box>
          </Box>

          {/* Upload progress bar */}
          {uploadProgress > 0 && (
            <Box sx={{ mt: 1.5 }}>
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
        </Paper>

        {/* Timestamp */}
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ mt: 0.5, px: 1 }}
        >
          {new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Typography>
      </Box>
    </Box>
  );
};

