import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  Button,
  Box,
  Typography,
  IconButton,
  Link,
  InputAdornment,
} from '@mui/material';
import {
  Close as CloseIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';

interface AddModelDialogProps {
  open: boolean;
  providerName: string;
  modelListUrl: string;
  onClose: () => void;
  onAddModel: (modelId: string) => void;
}

/**
 * AddModelDialog - Reusable dialog for adding models to a provider
 */
export const AddModelDialog = ({
  open,
  providerName,
  modelListUrl,
  onClose,
  onAddModel,
}: AddModelDialogProps) => {
  const [modelId, setModelId] = useState('');

  const handleAdd = () => {
    if (modelId.trim()) {
      onAddModel(modelId.trim());
      setModelId('');
      onClose();
    }
  };

  const handleClose = () => {
    setModelId('');
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      slotProps={{
        paper: {
          sx: {
            borderRadius: 2,
            p: 2,
          },
        },
      }}
    >
      <DialogTitle sx={{ p: 0, mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 0.5 }}>
            Add New Model
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Add a new model to the {providerName} provider.
          </Typography>
        </Box>
        <IconButton
          onClick={handleClose}
          size="small"
          sx={{ mt: -1, mr: -1 }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 500 }}>
            Model ID
            <Typography component="span" color="error.main" sx={{ ml: 0.5 }}>
              *
            </Typography>
          </Typography>

          <TextField
            fullWidth
            placeholder="Enter model ID"
            value={modelId}
            onChange={(e) => setModelId(e.target.value)}
            autoFocus
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton edge="end" size="small" sx={{ mr: 0.5 }}>
                      <RefreshIcon />
                    </IconButton>
                    <IconButton edge="end" size="small">
                      <ExpandMoreIcon />
                    </IconButton>
                  </InputAdornment>
                ),
              },
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'background.paper',
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              },
            }}
          />

          <Link
            href={modelListUrl}
            target="_blank"
            rel="noopener noreferrer"
            sx={{
              display: 'inline-block',
              mt: 1,
              fontSize: '0.875rem',
              color: 'primary.main',
              textDecoration: 'none',
              cursor: 'pointer',
              '&:hover': {
                textDecoration: 'underline',
              },
            }}
          >
            See model list from {providerName}
          </Link>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleAdd}
            disabled={!modelId.trim()}
            sx={{
              textTransform: 'none',
              px: 4,
              py: 1.5,
              fontSize: '1rem',
              fontWeight: 500,
              borderRadius: 2,
            }}
          >
            Add Model
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

