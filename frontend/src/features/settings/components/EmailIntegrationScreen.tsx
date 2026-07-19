import { useCallback, useEffect, useRef, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  IconButton,
  Snackbar,
  TextField,
  Typography,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Mail as MailIcon,
  ContentCopy,
  Sync as SyncIcon,
  LinkOff as LinkOffIcon,
  UploadFile as UploadFileIcon,
} from '@mui/icons-material';
import { UiIconButton, UiSectionTitle, UiEmptyState } from '../../../shared/components/ui';
import { useUserSelector } from '../../../shared/stores/userStore';
import { openExternal } from '../../../shared/utils';
import { EmailIntegrationApi } from '../../../data/api/EmailIntegrationApi';
import { useSettingsDispatch } from '../stores/settingsStore';
import { loadEmailAccounts } from '../stores/emailIntegrationSlice';
import { useLoadEmailAccounts } from '../hooks/useLoadEmailAccounts';
import type { EmailAccount } from '../types';
import { logger } from '../../../core/logger';

const GMAIL_PROVIDER = 'gmail';
const REDIRECT_URI = 'http://127.0.0.1:8001/api/email/oauth/callback';
const SYNC_POLL_INTERVAL_MS = 2500;

type OutletContext = {
  toggleDrawer: () => void;
  isConnected: boolean;
  isLargeScreen: boolean;
  connectionLabel: string;
};

const statusColor = (status: string): 'default' | 'success' | 'warning' | 'error' => {
  switch (status) {
    case 'connected':
      return 'success';
    case 'reauth_required':
      return 'warning';
    case 'error':
      return 'error';
    default:
      return 'default';
  }
};

export const EmailIntegrationScreen = () => {
  const { toggleDrawer, isLargeScreen, isConnected, connectionLabel } = useOutletContext<OutletContext>();
  const userId = useUserSelector((state) => state.user.userId);
  const dispatch = useSettingsDispatch();
  const { accounts, loading } = useLoadEmailAccounts(userId);

  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [isSavingCredentials, setIsSavingCredentials] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [syncingAccountIds, setSyncingAccountIds] = useState<Set<string>>(new Set());
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isImporting, setIsImporting] = useState(false);

  const showSnackbar = useCallback((message: string, severity: 'success' | 'error' = 'success') => {
    setSnackbar({ open: true, message, severity });
  }, []);

  const refreshAccounts = useCallback(() => {
    if (userId) dispatch(loadEmailAccounts(userId));
  }, [dispatch, userId]);

  // Poll sync status for any account currently running, until it settles.
  useEffect(() => {
    const runningIds = accounts.filter((a) => a.last_sync_status === 'running').map((a) => a.id);
    if (runningIds.length === 0) return;

    const interval = setInterval(async () => {
      let anyStillRunning = false;
      for (const accountId of runningIds) {
        try {
          const status = await EmailIntegrationApi.getSyncStatus(accountId);
          if (status.status === 'running') {
            anyStillRunning = true;
          }
        } catch (error) {
          logger.error('Failed to poll email sync status', error);
        }
      }
      refreshAccounts();
      if (!anyStillRunning) {
        setSyncingAccountIds(new Set());
      }
    }, SYNC_POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [accounts, refreshAccounts]);

  const handleSaveCredentials = async () => {
    if (!clientId.trim() || !clientSecret.trim()) {
      showSnackbar('Client ID and Client Secret are required', 'error');
      return;
    }
    setIsSavingCredentials(true);
    try {
      await EmailIntegrationApi.saveProviderCredentials({
        provider: GMAIL_PROVIDER,
        client_id: clientId.trim(),
        client_secret: clientSecret.trim(),
        redirect_uri: REDIRECT_URI,
      });
      showSnackbar('Google OAuth credentials saved');
      setClientSecret('');
    } catch (error) {
      logger.error('Failed to save email provider credentials', error);
      showSnackbar('Failed to save credentials', 'error');
    } finally {
      setIsSavingCredentials(false);
    }
  };

  const handleConnectGmail = async () => {
    if (!userId) return;
    setIsConnecting(true);
    try {
      const { auth_url } = await EmailIntegrationApi.getOAuthUrl(userId, GMAIL_PROVIDER);
      openExternal(auth_url);
      showSnackbar('Complete the Google sign-in in your browser, then return here.');
    } catch (error) {
      logger.error('Failed to start Gmail OAuth flow', error);
      showSnackbar('Failed to start Gmail connection - configure Client ID/Secret first', 'error');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleSyncNow = async (account: EmailAccount) => {
    try {
      await EmailIntegrationApi.startSync(account.id);
      setSyncingAccountIds((prev) => new Set(prev).add(account.id));
      refreshAccounts();
    } catch (error) {
      logger.error('Failed to start email sync', error);
      showSnackbar('Failed to start sync', 'error');
    }
  };

  const handleDisconnect = async (account: EmailAccount) => {
    try {
      await EmailIntegrationApi.disconnectAccount(account.id);
      showSnackbar(`Disconnected ${account.email_address}`);
      refreshAccounts();
    } catch (error) {
      logger.error('Failed to disconnect email account', error);
      showSnackbar('Failed to disconnect account', 'error');
    }
  };

  const handleImportFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file || !userId) return;

    const ext = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
    if (ext !== '.mbox' && ext !== '.eml') {
      showSnackbar('Only .mbox or .eml files are supported', 'error');
      return;
    }

    setIsImporting(true);
    try {
      await EmailIntegrationApi.importFile(userId, file);
      showSnackbar(`Importing ${file.name}...`);
      refreshAccounts();
    } catch (error) {
      logger.error('Failed to import email file', error);
      showSnackbar('Failed to import file', 'error');
    } finally {
      setIsImporting(false);
    }
  };

  const copyRedirectUri = async () => {
    await navigator.clipboard.writeText(REDIRECT_URI);
    showSnackbar('Redirect URI copied');
  };

  return (
    <Box sx={{ width: '100%', height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
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
          <Typography variant="h6" sx={{ flex: 1, fontWeight: 600 }}>
            Email Integrations
          </Typography>
          <Box
            sx={{
              px: 1.25,
              py: 0.6,
              borderRadius: '999px',
              border: '1px solid var(--border-subtle)',
              backgroundColor: 'color-mix(in srgb, var(--surface-secondary) 85%, transparent)',
              display: 'flex',
              alignItems: 'center',
              gap: 0.75,
              flexShrink: 0,
            }}
          >
            <Box sx={{ width: 7, height: 7, borderRadius: '50%', backgroundColor: isConnected ? 'success.main' : 'warning.main' }} />
            <Box component="span" sx={{ fontSize: '11px', fontWeight: 700, color: 'text.secondary', lineHeight: 1 }}>
              {connectionLabel}
            </Box>
          </Box>
        </Box>
      )}

      <Box sx={{ p: 3, maxWidth: 720, mx: 'auto', width: '100%' }}>
        <UiSectionTitle eyebrow="Integrations">Email Integrations</UiSectionTitle>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 3 }}>
          Connect Gmail or import email files so chat can answer questions grounded in your inbox.
        </Typography>

        {/* Google Cloud OAuth setup */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
            1. Google OAuth Setup (one time)
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            In Google Cloud Console: enable the Gmail API, set the OAuth consent screen to &quot;Testing&quot; with your
            own account as a test user, then create an OAuth Client ID of type &quot;Desktop app&quot;. Paste its
            Client ID and Client Secret below, and register the redirect URI shown below exactly as-is.
          </Alert>

          <Typography variant="subtitle2" sx={{ mb: 0.5 }}>Redirect URI (register this exactly in Google Cloud)</Typography>
          <TextField
            fullWidth
            value={REDIRECT_URI}
            slotProps={{ input: { readOnly: true, endAdornment: (
              <IconButton onClick={copyRedirectUri} edge="end" size="small">
                <ContentCopy fontSize="small" />
              </IconButton>
            ) } }}
            sx={{ mb: 2 }}
          />

          <Typography variant="subtitle2" sx={{ mb: 0.5 }}>Client ID</Typography>
          <TextField fullWidth value={clientId} onChange={(e) => setClientId(e.target.value)} sx={{ mb: 2 }} placeholder="xxxxx.apps.googleusercontent.com" />

          <Typography variant="subtitle2" sx={{ mb: 0.5 }}>Client Secret</Typography>
          <TextField fullWidth type="password" value={clientSecret} onChange={(e) => setClientSecret(e.target.value)} sx={{ mb: 2 }} />

          <Button variant="outlined" onClick={handleSaveCredentials} disabled={isSavingCredentials}>
            {isSavingCredentials ? <CircularProgress size={18} /> : 'Save Credentials'}
          </Button>
        </Box>

        <Divider sx={{ mb: 4 }} />

        {/* Connect + account list */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
            2. Connect Gmail
          </Typography>
          <Button variant="contained" startIcon={<MailIcon />} onClick={handleConnectGmail} disabled={isConnecting} sx={{ mb: 2 }}>
            {isConnecting ? <CircularProgress size={18} sx={{ color: 'inherit' }} /> : 'Connect Gmail'}
          </Button>

          {loading && accounts.length === 0 ? (
            <CircularProgress size={24} />
          ) : accounts.length === 0 ? (
            <UiEmptyState title="No email accounts connected" description="Connect Gmail above or import a file below." />
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {accounts.map((account) => {
                const isSyncing = account.last_sync_status === 'running' || syncingAccountIds.has(account.id);
                return (
                  <Box
                    key={account.id}
                    sx={{
                      p: 2,
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 2,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1.5,
                      flexWrap: 'wrap',
                    }}
                  >
                    <Box sx={{ flex: 1, minWidth: 200 }}>
                      <Typography variant="body1" sx={{ fontWeight: 600 }}>{account.email_address}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {account.provider === 'file_import' ? 'Imported file' : account.provider} &middot;{' '}
                        {account.last_synced_at ? `Last synced ${account.last_synced_at}` : 'Never synced'} &middot;{' '}
                        {account.total_messages_synced} messages
                      </Typography>
                      {account.last_sync_error && (
                        <Typography variant="body2" color="error.main">{account.last_sync_error}</Typography>
                      )}
                    </Box>
                    <Chip label={isSyncing ? 'syncing' : account.status} color={isSyncing ? 'default' : statusColor(account.status)} size="small" />
                    {account.provider !== 'file_import' && (
                      <Button
                        size="small"
                        startIcon={isSyncing ? <CircularProgress size={14} /> : <SyncIcon />}
                        onClick={() => handleSyncNow(account)}
                        disabled={isSyncing}
                      >
                        Sync Now
                      </Button>
                    )}
                    <IconButton size="small" onClick={() => handleDisconnect(account)} aria-label="disconnect">
                      <LinkOffIcon fontSize="small" />
                    </IconButton>
                  </Box>
                );
              })}
            </Box>
          )}
        </Box>

        <Divider sx={{ mb: 4 }} />

        {/* File import */}
        <Box>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
            Or import from a file
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
            No Google account needed - upload a .mbox export (e.g. from Google Takeout) or a single .eml file.
          </Typography>
          <input ref={fileInputRef} type="file" accept=".mbox,.eml" style={{ display: 'none' }} onChange={handleImportFile} />
          <Button variant="outlined" startIcon={isImporting ? <CircularProgress size={16} /> : <UploadFileIcon />} onClick={() => fileInputRef.current?.click()} disabled={isImporting}>
            Import from file
          </Button>
        </Box>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};
