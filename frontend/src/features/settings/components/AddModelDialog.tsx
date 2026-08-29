import { useCallback, useEffect, useRef, useState } from 'react';
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
  Menu,
  MenuItem,
  CircularProgress,
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
  /**
   * When provided, the refresh/dropdown adornments become functional: models
   * are fetched on open (and on refresh click) and offered in a picker menu.
   * Without it (providers with no listable local models), the adornments are
   * hidden and the dialog is a plain free-text input.
   */
  onFetchModels?: () => Promise<string[]>;
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
  onFetchModels,
}: AddModelDialogProps) => {
  const [modelId, setModelId] = useState('');
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [fetchingModels, setFetchingModels] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [menuAnchor, setMenuAnchor] = useState<HTMLElement | null>(null);

  // The parent typically passes an inline arrow for onFetchModels (new
  // reference every render), so the auto-fetch effect keys on `open` alone
  // and reads the latest fetcher through a ref - otherwise any parent
  // re-render while the dialog is open would re-trigger the fetch.
  const onFetchModelsRef = useRef(onFetchModels);
  onFetchModelsRef.current = onFetchModels;

  const fetchModels = useCallback(async () => {
    const fetcher = onFetchModelsRef.current;
    if (!fetcher) return;
    setFetchingModels(true);
    setFetchError(null);
    try {
      const models = await fetcher();
      setAvailableModels(models);
      if (models.length === 0) {
        setFetchError('No models installed - pull one first (e.g. `ollama pull llama3.2:3b`).');
      }
    } catch {
      setFetchError(`Could not load models from ${providerName} - is it running?`);
      setAvailableModels([]);
    } finally {
      setFetchingModels(false);
    }
  }, [providerName]);

  useEffect(() => {
    if (open && onFetchModelsRef.current) {
      fetchModels();
    }
  }, [open, fetchModels]);

  const handleAdd = () => {
    if (modelId.trim()) {
      onAddModel(modelId.trim());
      setModelId('');
      onClose();
    }
  };

  const handleClose = () => {
    setModelId('');
    setMenuAnchor(null);
    setFetchError(null);
    onClose();
  };

  const handlePickModel = (model: string) => {
    setModelId(model);
    setMenuAnchor(null);
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
                endAdornment: onFetchModels ? (
                  <InputAdornment position="end">
                    <IconButton
                      edge="end"
                      size="small"
                      sx={{ mr: 0.5 }}
                      onClick={fetchModels}
                      disabled={fetchingModels}
                      aria-label="refresh model list"
                    >
                      {fetchingModels ? <CircularProgress size={18} /> : <RefreshIcon />}
                    </IconButton>
                    <IconButton
                      edge="end"
                      size="small"
                      onClick={(e) => setMenuAnchor(e.currentTarget)}
                      disabled={fetchingModels || availableModels.length === 0}
                      aria-label="pick from installed models"
                    >
                      <ExpandMoreIcon />
                    </IconButton>
                  </InputAdornment>
                ) : undefined,
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

          <Menu
            anchorEl={menuAnchor}
            open={Boolean(menuAnchor)}
            onClose={() => setMenuAnchor(null)}
          >
            {availableModels.map((model) => (
              <MenuItem key={model} onClick={() => handlePickModel(model)}>
                {model}
              </MenuItem>
            ))}
          </Menu>

          {fetchError && (
            <Typography variant="body2" color="warning.main" sx={{ mt: 1 }}>
              {fetchError}
            </Typography>
          )}

          {modelListUrl && (
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
          )}
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
