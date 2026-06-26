import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
} from '@mui/material';
import {
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { logger } from '../../../core/logger';

interface ModelListProps {
  models: string[];
  providerName: string;
  selectedModel?: string | null;
  onStarModel?: (providerName: string, modelName: string | null) => void;
  onDeleteModel?: (providerName: string, modelName: string) => void;
}

/**
 * ModelList - Reusable component to display a list of models with star and delete actions
 */
export const ModelList = ({ models, providerName, selectedModel, onStarModel, onDeleteModel }: ModelListProps) => {
  const [starredModel, setStarredModel] = useState<string | null>(selectedModel || null);

  // Handle default selection: if there's only one model, select it by default
  useEffect(() => {
    if (models.length === 1 && !starredModel) {
      const defaultModel = models[0];
      setStarredModel(defaultModel);
      if (onStarModel) {
        onStarModel(providerName, defaultModel);
      }
    }
  }, [models, starredModel, providerName, onStarModel]);

  // Sync with selectedModel prop when it changes
  useEffect(() => {
    setStarredModel(selectedModel || null);
  }, [selectedModel]);

  if (models.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
        No models added yet. Click the + icon to add a model.
      </Typography>
    );
  }

  const handleStarClick = (modelName: string) => {
    logger.info('Star model clicked', { provider: providerName, model: modelName });

    // Toggle starred state - only one model can be starred at a time
    const newStarredModel = starredModel === modelName ? null : modelName;
    setStarredModel(newStarredModel);

    if (onStarModel) {
      onStarModel(providerName, newStarredModel);
    }
  };

  const handleDeleteClick = (modelName: string) => {
    logger.info('Delete model clicked', { provider: providerName, model: modelName });
    if (onDeleteModel) {
      onDeleteModel(providerName, modelName);
    }
  };

  return (
    <List sx={{ p: 0 }}>
      {models.map((modelName, index) => (
        <ListItem
          key={`${modelName}-${index}`}
          sx={{
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
            mb: 1,
            '&:last-child': {
              mb: 0,
            },
            '&:hover': {
              backgroundColor: 'action.hover',
            },
          }}
          secondaryAction={
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton
                edge="end"
                aria-label="favorite"
                size="small"
                onClick={() => handleStarClick(modelName)}
                sx={{
                  color: 'primary.main',
                }}
              >
                {starredModel === modelName ? (
                  <StarIcon fontSize="small" />
                ) : (
                  <StarBorderIcon fontSize="small" />
                )}
              </IconButton>
              <IconButton
                edge="end"
                aria-label="delete"
                size="small"
                onClick={() => handleDeleteClick(modelName)}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Box>
          }
        >
          <ListItemText
            primary={modelName}
            slotProps={{
              primary: {
                fontWeight: 500,
              }
            }}
          />
        </ListItem>
      ))}
    </List>
  );
};

