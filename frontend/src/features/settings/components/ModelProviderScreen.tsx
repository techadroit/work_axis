import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Alert,
  Fab,
  Snackbar,
  IconButton,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Save as SaveIcon,
  CheckCircle as CheckCircleIcon,
  Add as AddIcon,
  Check as CheckIcon,
  Menu as MenuIcon,
} from '@mui/icons-material';
import { useOutletContext } from 'react-router-dom';
import { useLoadModelProviders } from '../hooks/useLoadModelProviders';
import { useSettingsDispatch, useSettingsSelector } from '../stores/settingsStore';
import { loadSavedProviders } from '../stores/modelProviderSlice';
import { ModelProviderApi } from '../../../data/api/ModelProviderApi';
import { ProviderField } from './ProviderField';
import { AddModelDialog } from './AddModelDialog';
import { ModelList } from './ModelList';
import type { SaveProviderRequest } from '../types';
import { logger } from '../../../core/logger';
import { UiEmptyState, UiSectionTitle, UiIconButton } from '../../../shared/components/ui';

/**
 * ModelProviderScreen - Displays model providers in an expandable list
 */
export const ModelProviderScreen = () => {
  const { providers, loading, error } = useLoadModelProviders();
  const dispatch = useSettingsDispatch();
  const { savedProviders, loadingSavedProviders } = useSettingsSelector((state) => state.modelProvider);

  // Outlet context from MainScreen for small-screen drawer toggle
  const { toggleDrawer, isLargeScreen, isConnected, connectionLabel } =
    useOutletContext<{ toggleDrawer: () => void; isLargeScreen: boolean; isConnected: boolean; connectionLabel: string }>();

  const [expanded, setExpanded] = useState<string | false>(false);
  const [visibleFields, setVisibleFields] = useState<Record<string, boolean>>({});
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({});
  const [modelLists, setModelLists] = useState<Record<string, string[]>>({});
  const [selectedModels, setSelectedModels] = useState<Record<string, string | null>>({});
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [addModelDialogOpen, setAddModelDialogOpen] = useState(false);
  const [selectedProviderData, setSelectedProviderData] = useState<{ name: string; modelListUrl: string }>({
    name: '',
    modelListUrl: '',
  });

  // Load saved providers on mount
  useEffect(() => {
    dispatch(loadSavedProviders());
  }, [dispatch]);

  // Populate field values when saved providers are loaded
  useEffect(() => {
    if (savedProviders.length > 0) {
      const initialValues: Record<string, string> = {};
      const initialModelLists: Record<string, string[]> = {};
      const initialSelectedModels: Record<string, string | null> = {};
      let primaryProvider: string | null = null;

      savedProviders.forEach((savedProvider) => {
        const providerName = savedProvider.provider_name;

        // Map API response fields to form fields
        const fieldMapping: Record<string, string | null> = {
          'api_key': savedProvider.api_key,
          'base_url': savedProvider.base_url,
          'api_version': savedProvider.api_version,
          'deployment_name': savedProvider.deployment_name,
          'aws_access_key_id': savedProvider.aws_access_key_id,
          'aws_secret_access_key': savedProvider.aws_secret_access_key,
          'model_provider': savedProvider.model_provider,
          'region': savedProvider.region,
        };

        // Populate form fields with saved values
        Object.entries(fieldMapping).forEach(([fieldName, fieldValue]) => {
          if (fieldValue !== null) {
            const fieldKey = `${providerName}-${fieldName}`;
            initialValues[fieldKey] = fieldValue;
          }
        });

        // Populate model lists
        if (savedProvider.model_list && savedProvider.model_list.length > 0) {
          initialModelLists[providerName] = savedProvider.model_list;
        }

        // Populate selected model
        if (savedProvider.selected_model) {
          initialSelectedModels[providerName] = savedProvider.selected_model;
        }

        // Set primary provider
        if (savedProvider.is_primary) {
          primaryProvider = providerName;
        }
      });

      setFieldValues(initialValues);
      setModelLists(initialModelLists);
      setSelectedModels(initialSelectedModels);
      setSelectedProvider(primaryProvider);
      logger.info('Populated form with saved provider configurations', { count: savedProviders.length, primaryProvider });
    }
  }, [savedProviders]);

  const handleAccordionChange = (providerName: string) => (_event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded ? providerName : false);
  };

  const handleSelectProvider = (providerName: string) => {
    // Toggle: if already selected, unselect; otherwise select this provider
    setSelectedProvider(prev => prev === providerName ? null : providerName);
    setHasUnsavedChanges(true);
  };

  const toggleFieldVisibility = (fieldKey: string) => {
    setVisibleFields(prev => ({ ...prev, [fieldKey]: !prev[fieldKey] }));
  };

  const handleCopyToClipboard = (value: string) => {
    navigator.clipboard.writeText(value);
  };

  const handleFieldChange = (fieldKey: string, value: string) => {
    setFieldValues(prev => ({ ...prev, [fieldKey]: value }));
    setHasUnsavedChanges(true);
  };

  const handleSave = async () => {
    // Validate that at least one provider is selected
    if (!selectedProvider) {
      setSnackbarMessage('Please select a primary provider before saving.');
      setSnackbarOpen(true);
      return;
    }

    setIsSaving(true);
    logger.info('Saving model provider configurations', { fieldCount: Object.keys(fieldValues).length, selectedProvider });

    try {
      // Transform fieldValues into API payload format
      // Group fields by provider name
      const providerConfigs: Record<string, SaveProviderRequest> = {};

      Object.entries(fieldValues).forEach(([fieldKey, fieldValue]) => {
        // Parse field key: "ProviderName-fieldName"
        // Use lastIndexOf to correctly handle provider names that contain hyphens
        const separatorIndex = fieldKey.lastIndexOf('-');
        if (separatorIndex === -1) return;

        const providerName = fieldKey.substring(0, separatorIndex);
        const fieldName = fieldKey.substring(separatorIndex + 1);

        // Initialize provider config if not exists
        if (!providerConfigs[providerName]) {
          providerConfigs[providerName] = {
            provider_name: providerName,
          };
        }

        // Set field value (only if not empty)
        if (fieldValue && fieldValue.trim()) {
          (providerConfigs[providerName] as any)[fieldName] = fieldValue.trim();
        }
      });

      // Add model lists to provider configs
      Object.entries(modelLists).forEach(([providerName, models]) => {
        if (!providerConfigs[providerName]) {
          providerConfigs[providerName] = {
            provider_name: providerName,
          };
        }

        // Only add model_list if it has items
        if (models && models.length > 0) {
          providerConfigs[providerName].model_list = models;
        }
      });

      // Add selected models to provider configs
      Object.entries(selectedModels).forEach(([providerName, selectedModel]) => {
        if (!providerConfigs[providerName]) {
          providerConfigs[providerName] = {
            provider_name: providerName,
          };
        }

        // Add selected_model field (can be null)
        providerConfigs[providerName].selected_model = selectedModel;
      });

      // Add is_primary field to all provider configs
      Object.keys(providerConfigs).forEach((providerName) => {
        providerConfigs[providerName].is_primary = providerName === selectedProvider;
      });

      // Convert to array and filter out providers with only provider_name
      const payload = Object.values(providerConfigs).filter(config => {
        // Check if config has at least one field other than provider_name
        return Object.keys(config).length > 1;
      });

      logger.info('Transformed payload for save', { providerCount: payload.length, primaryProvider: selectedProvider, payload });

      // Call API to save configurations
      const savedProviders = await ModelProviderApi.saveProviders(payload);

      logger.info('Model provider configurations saved successfully', { count: savedProviders.length });

      // Reload saved providers to get updated data with IDs
      await dispatch(loadSavedProviders());

      setSnackbarMessage('Settings saved successfully!');
      setSnackbarOpen(true);
      setHasUnsavedChanges(false);
    } catch (err) {
      logger.error('Failed to save model provider configurations', err);
      setSnackbarMessage('Failed to save settings. Please try again.');
      setSnackbarOpen(true);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleOpenAddModelDialog = (providerName: string, modelListUrl: string) => {
    setSelectedProviderData({ name: providerName, modelListUrl });
    setAddModelDialogOpen(true);
  };

  const handleCloseAddModelDialog = () => {
    setAddModelDialogOpen(false);
    setSelectedProviderData({ name: '', modelListUrl: '' });
  };

  const handleAddModel = (modelId: string) => {
    const providerName = selectedProviderData.name;
    logger.info('Adding model to provider', { provider: providerName, modelId });

    // Add model to the modelLists state
    setModelLists(prev => {
      const currentModels = prev[providerName] || [];

      // Check if model already exists
      if (currentModels.includes(modelId)) {
        logger.warn('Model already exists in list', { provider: providerName, model: modelId });
        return prev;
      }

      return {
        ...prev,
        [providerName]: [...currentModels, modelId],
      };
    });

    setHasUnsavedChanges(true);
    setSnackbarMessage(`Model "${modelId}" added to ${providerName}`);
    setSnackbarOpen(true);
  };

  const handleStarModel = (providerName: string, modelName: string | null) => {
    logger.info('Star/favorite model', { provider: providerName, model: modelName });

    // Update selected model for this provider
    setSelectedModels(prev => ({
      ...prev,
      [providerName]: modelName,
    }));

    setHasUnsavedChanges(true);

    if (modelName) {
      setSnackbarMessage(`Model "${modelName}" selected as favorite`);
    } else {
      setSnackbarMessage(`Model unselected`);
    }
    setSnackbarOpen(true);
  };

  const handleDeleteModel = (providerName: string, modelName: string) => {
    logger.info('Delete model', { provider: providerName, model: modelName });

    // Remove model from the modelLists state
    setModelLists(prev => {
      const currentModels = prev[providerName] || [];
      const updatedModels = currentModels.filter(model => model !== modelName);

      return {
        ...prev,
        [providerName]: updatedModels,
      };
    });

    // If the deleted model was selected, clear the selection
    setSelectedModels(prev => {
      if (prev[providerName] === modelName) {
        return {
          ...prev,
          [providerName]: null,
        };
      }
      return prev;
    });

    setHasUnsavedChanges(true);
    setSnackbarMessage(`Model "${modelName}" deleted from ${providerName}`);
    setSnackbarOpen(true);
  };


  if (loading || loadingSavedProviders) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100%',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <Alert severity="error">
          <Typography variant="body1">Failed to load model providers</Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            {error}
          </Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <>
      {/* Small-screen header with hamburger */}
      {!isLargeScreen && (
        <Box
          sx={{
            px: 1.5,
            py: 1,
            borderBottom: '1px solid var(--border-subtle)',
            backgroundColor: 'color-mix(in srgb, var(--surface-primary) 78%, transparent)',
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            flexShrink: 0,
          }}
        >
          <UiIconButton tone="ghost" size="small" aria-label="open navigation" onClick={toggleDrawer} sx={{ flexShrink: 0 }}>
            <MenuIcon />
          </UiIconButton>
          <Typography variant="h6" sx={{ flex: 1, fontWeight: 600 }}>Model Providers</Typography>
          <Box
            sx={{
              px: 1.25, py: 0.6, borderRadius: '999px',
              border: '1px solid var(--border-subtle)',
              backgroundColor: 'color-mix(in srgb, var(--surface-secondary) 85%, transparent)',
              display: 'flex', alignItems: 'center', gap: 0.75, flexShrink: 0,
            }}
          >
            <Box sx={{ width: 7, height: 7, borderRadius: '50%', backgroundColor: isConnected ? 'success.main' : 'warning.main' }} />
            <Box component="span" sx={{ fontSize: '11px', fontWeight: 700, color: 'text.secondary', lineHeight: 1 }}>
              {connectionLabel}
            </Box>
          </Box>
        </Box>
      )}

      <Box sx={{ width: '100%', height: '100%', overflow: 'auto', p: { xs: 2, sm: 2.5, md: 3 }, pb: 12 }}>
          <UiSectionTitle eyebrow="Providers">
            Model Providers
          </UiSectionTitle>

          <Typography variant="body1" color="text.secondary" sx={{ mt: 1.25, mb: 4 }}>
            Configure your AI model providers. Select a provider below to view and edit its configuration.
          </Typography>

          {providers.length === 0 ? (
            <UiEmptyState
              title="No model providers available"
              description="Provider definitions will appear here when the configuration metadata is available."
              sx={{ minHeight: 260 }}
            />
          ) : (
            <Box>
              {providers.map((provider) => (
                <Accordion
                  key={provider.name}
                  expanded={expanded === provider.name}
                  onChange={handleAccordionChange(provider.name)}
                  sx={{
                    mb: 2,
                    '&:before': {
                      display: 'none',
                    },
                    boxShadow: 'none',
                    borderRadius: '20px',
                    border: '1px solid var(--border-subtle)',
                    backgroundColor: 'color-mix(in srgb, var(--surface-primary) 88%, transparent)',
                    '&.Mui-expanded': {
                      boxShadow: 'var(--shadow-soft)',
                    },
                  }}
                >
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon />}
                    sx={{
                      '& .MuiAccordionSummary-content': {
                        my: 1.5,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      },
                      '&:hover': {
                        backgroundColor: 'color-mix(in srgb, var(--accent-primary) 6%, transparent)',
                      },
                    }}
                  >
                    <Typography variant="h6" sx={{ fontWeight: 500 }}>
                      {provider.name}
                    </Typography>
                    <IconButton
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSelectProvider(provider.name);
                      }}
                      sx={{
                        mr: 1,
                        color: selectedProvider === provider.name ? 'primary.main' : 'action.disabled',
                        '&:hover': {
                          backgroundColor: 'action.hover',
                        },
                        p: { xs: 0.5, sm: 0.75, md: 1 },
                      }}
                    >
                      <CheckIcon sx={{
                        fontSize: { xs: 12, sm: 16, md: 24, lg: 32 },
                        strokeWidth: 2,
                        stroke: 'currentColor',
                      }} />
                    </IconButton>
                  </AccordionSummary>
                  <AccordionDetails sx={{ pt: 2, pb: 3, px: 3 }}>
                    {provider.fields.map((field) => {
                      const fieldKey = `${provider.name}-${field.name}`;
                      const fieldValue = fieldValues[fieldKey] || field.default || '';
                      const isPasswordVisible = visibleFields[fieldKey] || false;

                      return (
                        <ProviderField
                          key={field.name}
                          field={field}
                          fieldKey={fieldKey}
                          fieldValue={fieldValue}
                          isPasswordVisible={isPasswordVisible}
                          onToggleVisibility={toggleFieldVisibility}
                          onCopyToClipboard={handleCopyToClipboard}
                          onFieldChange={handleFieldChange}
                        />
                      );
                    })}

                    {/* Models Section */}
                    <Box sx={{ mt: 4, pt: 3, borderTop: '1px solid', borderColor: 'divider' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                        <Typography variant="h6" sx={{ fontWeight: 500 }}>
                          Models
                        </Typography>
                        <IconButton
                          onClick={() => handleOpenAddModelDialog(provider.name, provider.model_list)}
                          size="small"
                          sx={{
                            backgroundColor: 'color-mix(in srgb, var(--surface-secondary) 85%, transparent)',
                            '&:hover': {
                              backgroundColor: 'color-mix(in srgb, var(--accent-primary) 12%, transparent)',
                            },
                          }}
                        >
                          <AddIcon />
                        </IconButton>
                      </Box>

                      {/* Display models from saved provider */}
                      <ModelList
                        models={modelLists[provider.name] || []}
                        providerName={provider.name}
                        selectedModel={selectedModels[provider.name]}
                        onStarModel={handleStarModel}
                        onDeleteModel={handleDeleteModel}
                      />
                    </Box>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </Box>

      {/* Sticky Save Button */}
      <Fab
        color="primary"
        variant="extended"
        onClick={handleSave}
        disabled={isSaving || !hasUnsavedChanges}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          boxShadow: 4,
          '&:hover': {
            boxShadow: 6,
          },
          minWidth: 120,
        }}
      >
        {isSaving ? (
          <>
            <CircularProgress size={20} sx={{ mr: 1 }} color="inherit" />
            Saving...
          </>
        ) : hasUnsavedChanges ? (
          <>
            <SaveIcon sx={{ mr: 1 }} />
            Save
          </>
        ) : (
          <>
            <CheckCircleIcon sx={{ mr: 1 }} />
            Saved
          </>
        )}
      </Fab>

      {/* Snackbar for save notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={handleSnackbarClose}
        message={snackbarMessage}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />

      {/* Add Model Dialog */

      }
      <AddModelDialog
        open={addModelDialogOpen}
        providerName={selectedProviderData.name}
        modelListUrl={selectedProviderData.modelListUrl}
        onClose={handleCloseAddModelDialog}
        onAddModel={handleAddModel}
      />
    </>
  );
};

