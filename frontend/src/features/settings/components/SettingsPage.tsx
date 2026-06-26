import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Alert,
  Snackbar,
} from '@mui/material';
import { Delete as DeleteIcon, Warning as WarningIcon, Menu as MenuIcon } from '@mui/icons-material';
import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { logger } from '../../../core/logger';
import { UiDivider, UiIconButton, UiSectionTitle } from '../../../shared/components/ui';

/**
 * SettingsPage - Application settings and data management
 */
export const SettingsPage = () => {
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');

  const { toggleDrawer, isLargeScreen, isConnected, connectionLabel } =
    useOutletContext<{ toggleDrawer: () => void; isLargeScreen: boolean; isConnected: boolean; connectionLabel: string }>();

  const handleClearDataClick = () => {
    setConfirmDialogOpen(true);
  };

  const handleConfirmClearData = () => {
    try {
      logger.info('Clearing all application data');

      // Clear all localStorage items
      const localStorageKeys = Object.keys(localStorage);
      localStorageKeys.forEach(key => {
        localStorage.removeItem(key);
      });
      logger.info(`Cleared ${localStorageKeys.length} localStorage items`);

      // Clear all sessionStorage items
      const sessionStorageKeys = Object.keys(sessionStorage);
      sessionStorageKeys.forEach(key => {
        sessionStorage.removeItem(key);
      });
      logger.info(`Cleared ${sessionStorageKeys.length} sessionStorage items`);

      // Clear all cookies
      const cookies = document.cookie.split(';');
      cookies.forEach(cookie => {
        const cookieName = cookie.split('=')[0].trim();
        // Set cookie to expire in the past
        document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        // Also try with domain
        document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${window.location.hostname}`;
      });
      logger.info(`Cleared ${cookies.length} cookies`);

      // Clear IndexedDB databases (if any)
      if (window.indexedDB) {
        window.indexedDB.databases().then(databases => {
          databases.forEach(db => {
            if (db.name) {
              window.indexedDB.deleteDatabase(db.name);
              logger.info(`Deleted IndexedDB database: ${db.name}`);
            }
          });
        }).catch(error => {
          logger.warn('Could not clear IndexedDB', error);
        });
      }

      setConfirmDialogOpen(false);
      setSnackbarMessage('All data cleared successfully! Reloading application...');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);

      // Reload the application after a short delay
      setTimeout(() => {
        window.location.href = '/';
      }, 2000);

    } catch (error) {
      logger.error('Failed to clear data', error);
      setConfirmDialogOpen(false);
      setSnackbarMessage('Failed to clear data. Please try again.');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };

  const handleCancelClearData = () => {
    setConfirmDialogOpen(false);
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden', bgcolor: 'primary_bg.main' }}>
      {/* Small-screen header with hamburger */}
      {!isLargeScreen && (
        <Box
          sx={{
            px: 1.5,
            py: 1,
            borderBottom: '1px solid var(--border-subtle)',
            backgroundColor: 'primary_bg.main',
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            flexShrink: 0,
          }}
        >
          <UiIconButton tone="ghost" size="small" aria-label="open navigation" onClick={toggleDrawer} sx={{ flexShrink: 0 }}>
            <MenuIcon />
          </UiIconButton>
          <Typography variant="h6" sx={{ flex: 1, fontWeight: 600 }}>Settings</Typography>
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

      {/* Scrollable content */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: { xs: 2, sm: 2.5, md: 3 },
          bgcolor: 'primary_bg.main',
        }}
      >
        <Box sx={{ mb: 2.5 }}>
          <UiSectionTitle eyebrow="Preferences">
            Settings
          </UiSectionTitle>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1.25, maxWidth: 720 }}>
            Manage local app data and prepare the client for provider-level configuration without changing the existing behavior of the application.
          </Typography>
        </Box>

        {/* Full-width divider between header and settings list */}
        <UiDivider sx={{ mx: { xs: -2, sm: -2.5, md: -3 }, mb: 0 }} />

        {/* Settings list with inset item dividers */}
        <Box sx={{ maxWidth: 860 }}>
          <Box sx={{ px: { xs: 1, sm: 2 }, py: 2.5 }}>

            {/* Data Management Section */}
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Data Management
            </Typography>

            <Box
              sx={{
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                gap: 2,
                flexDirection: { xs: 'column', md: 'row' },
              }}
            >
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 500, mb: 1 }}>
                  Clear All Data
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Remove all stored data including cookies, local storage, and session data.
                  This will log you out and reset the application to its initial state.
                </Typography>
                <Alert severity="warning" icon={<WarningIcon />} sx={{ mb: 2 }}>
                  This action cannot be undone. All your chat sessions, preferences, and cached data will be permanently deleted.
                </Alert>
              </Box>

              <Button
                variant="outlined"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={handleClearDataClick}
                sx={{
                  minWidth: 150,
                  flexShrink: 0,
                }}
              >
                Clear Data
              </Button>
            </Box>
          </Box>

          <UiDivider insetX={{ xs: 1, sm: 2 }} />

          <Box sx={{ px: { xs: 1, sm: 2 }, py: 2.5 }}>
            {/* Future Settings Sections */}
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Application Settings
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Additional settings will appear here in future updates.
            </Typography>
          </Box>
        </Box>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={handleCancelClearData}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <WarningIcon color="warning" />
          Confirm Clear Data
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to clear all application data? This will:
          </DialogContentText>
          <Box component="ul" sx={{ mt: 2, pl: 2 }}>
            <li>
              <Typography variant="body2">Delete all cookies</Typography>
            </li>
            <li>
              <Typography variant="body2">Clear all local storage data</Typography>
            </li>
            <li>
              <Typography variant="body2">Remove all session data</Typography>
            </li>
            <li>
              <Typography variant="body2">Delete cached database information</Typography>
            </li>
            <li>
              <Typography variant="body2">Log you out of the application</Typography>
            </li>
          </Box>
          <Alert severity="error" sx={{ mt: 2 }}>
            This action is permanent and cannot be undone!
          </Alert>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleCancelClearData} variant="outlined">
            Cancel
          </Button>
          <Button
            onClick={handleConfirmClearData}
            variant="contained"
            color="error"
            startIcon={<DeleteIcon />}
          >
            Clear All Data
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
      </Box>
    </Box>
  );
};

