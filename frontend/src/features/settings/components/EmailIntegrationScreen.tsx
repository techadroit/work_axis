import { useCallback, useEffect, useRef, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Collapse,
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
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { UiIconButton, UiSectionTitle, UiEmptyState } from '../../../shared/components/ui';
import { useUserSelector } from '../../../shared/stores/userStore';
import { openExternal } from '../../../shared/utils';
import { EmailIntegrationApi } from '../../../data/api/EmailIntegrationApi';
import { useSettingsDispatch } from '../stores/settingsStore';
import { loadEmailAccounts } from '../stores/emailIntegrationSlice';
import { useLoadEmailAccounts } from '../hooks/useLoadEmailAccounts';
import type { EmailAccount, EmailProviderStatus } from '../types';
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
  const [awaitingAuthorization, setAwaitingAuthorization] = useState(false);
  const [providerStatus, setProviderStatus] = useState<EmailProviderStatus | null>(null);
  const [loadingProviderStatus, setLoadingProviderStatus] = useState(true);
  const [showAdvancedSetup, setShowAdvancedSetup] = useState(false);
  const [syncingAccountIds, setSyncingAccountIds] = useState<Set<string>>(new Set());
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isImporting, setIsImporting] = useState(false);
  const preAuthGmailCountRef = useRef(0);

  const gmailAccounts = accounts.filter((a) => a.provider === GMAIL_PROVIDER);
  const fileImportAccounts = accounts.filter((a) => a.provider === 'file_import');

  const showSnackbar = useCallback((message: string, severity: 'success' | 'error' = 'success') => {
    setSnackbar({ open: true, message, severity });
  }, []);

  const refreshAccounts = useCallback(() => {
    if (userId) dispatch(loadEmailAccounts(userId));
  }, [dispatch, userId]);

  const refreshProviderStatus = useCallback(async () => {
    setLoadingProviderStatus(true);
    try {
      const status = await EmailIntegrationApi.getProviderStatus(GMAIL_PROVIDER);
      setProviderStatus(status);
      // Only auto-open the manual entry form when there's truly no way to
      // connect yet (no bundled default, nothing saved) - otherwise it stays
      // tucked away under "Advanced" since most users never need it.
      if (!status.available) setShowAdvancedSetup(true);
    } catch (error) {
      logger.error('Failed to load email provider status', error);
      // Fail open to the manual form rather than silently blocking "Connect
      // Gmail" behind a status check that itself failed.
      setProviderStatus({ provider: GMAIL_PROVIDER, available: false, source: 'none' });
      setShowAdvancedSetup(true);
    } finally {
      setLoadingProviderStatus(false);
    }
  }, []);

  useEffect(() => {
    refreshProviderStatus();
  }, [refreshProviderStatus]);

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

  // While waiting for the user to finish the Google consent screen in their
  // browser, poll the account list so "Connected" appears on its own - the
  // same "click Connect, it just updates when you're done" feel as Claude's
  // own connector list, instead of making the user come back and hit refresh.
  useEffect(() => {
    if (!awaitingAuthorization) return;
    const startedAt = Date.now();
    const interval = setInterval(() => {
      refreshAccounts();
      if (Date.now() - startedAt > 90_000) {
        setAwaitingAuthorization(false);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [awaitingAuthorization, refreshAccounts]);

  useEffect(() => {
    if (!awaitingAuthorization) return;
    if (gmailAccounts.length > preAuthGmailCountRef.current) {
      setAwaitingAuthorization(false);
      showSnackbar('Gmail connected');
    }
  }, [awaitingAuthorization, gmailAccounts.length, showSnackbar]);

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
      refreshProviderStatus();
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
      preAuthGmailCountRef.current = gmailAccounts.length;
      openExternal(auth_url);
      setAwaitingAuthorization(true);
      showSnackbar('Complete the Google sign-in in your browser - this updates automatically.');
    } catch (error) {
      logger.error('Failed to start Gmail OAuth flow', error);
      showSnackbar(
        providerStatus?.available ? 'Failed to start Gmail connection' : 'Configure a Google OAuth Client ID/Secret first',
        'error'
      );
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

  const renderAccountRow = (account: EmailAccount) => {
    const isSyncing = account.last_sync_status === 'running' || syncingAccountIds.has(account.id);
    return (
      <Box
        key={account.id}
        sx={{
          p: 1.5,
          border: '1px solid var(--border-subtle)',
          borderRadius: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          flexWrap: 'wrap',
        }}
      >
        <Box sx={{ flex: 1, minWidth: 200 }}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>{account.email_address}</Typography>
          <Typography variant="caption" color="text.secondary">
            {account.last_synced_at ? `Last synced ${account.last_synced_at}` : 'Never synced'} &middot;{' '}
            {account.total_messages_synced} messages
          </Typography>
          {account.last_sync_error && (
            <Typography variant="caption" color="error.main" sx={{ display: 'block' }}>{account.last_sync_error}</Typography>
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

        <Typography variant="overline" sx={{ color: 'text.secondary', fontWeight: 700, letterSpacing: '0.06em' }}>
          Connectors
        </Typography>

        {/* Gmail connector card */}
        <Box
          sx={{
            mt: 1,
            mb: 3,
            p: 2.5,
            border: '1px solid var(--border-subtle)',
            borderRadius: '20px',
            backgroundColor: 'color-mix(in srgb, var(--surface-primary) 88%, transparent)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
            <Box
              sx={{
                width: 44,
                height: 44,
                borderRadius: '12px',
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'color-mix(in srgb, #EA4335 14%, transparent)',
              }}
            >
              <MailIcon sx={{ color: '#EA4335' }} />
            </Box>

            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Gmail</Typography>
                {awaitingAuthorization ? (
                  <Chip label="Connecting…" size="small" color="info" />
                ) : gmailAccounts.length === 0 ? (
                  <Chip label="Not connected" size="small" variant="outlined" />
                ) : null}
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.25 }}>
                Search your inbox from chat - read-only access, disconnect anytime.
              </Typography>

              {loadingProviderStatus || loading ? (
                <CircularProgress size={18} sx={{ mt: 1.5 }} />
              ) : (
                <>
                  {providerStatus?.source === 'none' && (
                    <Alert severity="warning" sx={{ mt: 1.5, mb: 1 }}>
                      No Google connection is configured for this app yet. Use &quot;Advanced&quot; below to add your
                      own Google Cloud OAuth client.
                    </Alert>
                  )}

                  <Box sx={{ mt: 1.5, display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap' }}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={isConnecting || awaitingAuthorization ? undefined : <MailIcon />}
                      onClick={handleConnectGmail}
                      disabled={isConnecting || awaitingAuthorization || !providerStatus?.available}
                    >
                      {isConnecting || awaitingAuthorization ? (
                        <CircularProgress size={16} sx={{ color: 'inherit' }} />
                      ) : gmailAccounts.length > 0 ? (
                        'Connect another account'
                      ) : (
                        'Connect'
                      )}
                    </Button>
                    {providerStatus?.source === 'custom' && (
                      <Typography variant="caption" color="text.secondary">Using your own Google Cloud OAuth client</Typography>
                    )}
                  </Box>
                </>
              )}

              {gmailAccounts.length > 0 && (
                <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {gmailAccounts.map(renderAccountRow)}
                </Box>
              )}

              {/* Advanced: use a self-hosted Google Cloud OAuth client instead
                  of this app's bundled default - only needed to raise the
                  100-test-user cap on your own Google Cloud project, or to
                  keep the OAuth client under your own control. */}
              <Box sx={{ mt: 2 }}>
                <Button
                  size="small"
                  onClick={() => setShowAdvancedSetup((prev) => !prev)}
                  endIcon={
                    <ExpandMoreIcon
                      fontSize="small"
                      sx={{ transform: showAdvancedSetup ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}
                    />
                  }
                  sx={{ textTransform: 'none', color: 'text.secondary', pl: 0 }}
                >
                  Advanced: use your own Google Cloud project
                </Button>
                <Collapse in={showAdvancedSetup}>
                  <Box sx={{ mt: 1, p: 2, border: '1px solid var(--border-subtle)', borderRadius: 2 }}>
                    <Alert severity="info" sx={{ mb: 2 }}>
                      In Google Cloud Console: enable the Gmail API, set the OAuth consent screen to &quot;Testing&quot; with your
                      own account as a test user, then create an OAuth Client ID of type &quot;Desktop app&quot;. Paste its
                      Client ID and Client Secret below, and register the redirect URI shown below exactly as-is. This
                      overrides the app's built-in Google connection for every user of this install.
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
                </Collapse>
              </Box>
            </Box>
          </Box>
        </Box>

        {/* File import connector card */}
        <Box
          sx={{
            p: 2.5,
            border: '1px solid var(--border-subtle)',
            borderRadius: '20px',
            backgroundColor: 'color-mix(in srgb, var(--surface-primary) 88%, transparent)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
            <Box
              sx={{
                width: 44,
                height: 44,
                borderRadius: '12px',
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'color-mix(in srgb, var(--accent-primary) 14%, transparent)',
              }}
            >
              <UploadFileIcon color="primary" />
            </Box>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Import from file</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.25, mb: 1.5 }}>
                No Google account needed - upload a .mbox export (e.g. from Google Takeout) or a single .eml file.
              </Typography>
              <input ref={fileInputRef} type="file" accept=".mbox,.eml" style={{ display: 'none' }} onChange={handleImportFile} />
              <Button
                variant="contained"
                size="small"
                startIcon={isImporting ? undefined : <UploadFileIcon />}
                onClick={() => fileInputRef.current?.click()}
                disabled={isImporting}
              >
                {isImporting ? <CircularProgress size={16} sx={{ color: 'inherit' }} /> : 'Import from file'}
              </Button>

              {fileImportAccounts.length > 0 && (
                <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {fileImportAccounts.map(renderAccountRow)}
                </Box>
              )}
            </Box>
          </Box>
        </Box>

        {accounts.length === 0 && !loading && (
          <UiEmptyState
            sx={{ mt: 3 }}
            title="No email accounts connected"
            description="Connect Gmail or import a file above to get started."
          />
        )}
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
