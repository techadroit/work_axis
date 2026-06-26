import {
  Drawer,
  List,
  Box,
  Divider,
  useTheme,
  useMediaQuery,
  CircularProgress,
  InputBase,
  Typography,
} from '@mui/material';
import {
  Home as HomeIcon,
  Settings as SettingsIcon,
  ChevronLeft as ChevronLeftIcon,
  Menu as MenuIcon,
  Add as AddIcon,
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { alpha } from '@mui/material/styles';
import { useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { NavigationItem } from './navigation-item.tsx';
import { ChatSessionList } from './ChatSessionList.tsx';
import { SettingsItemList } from './SettingsItemList.tsx';
import { useChatSessionDispatch, useChatSessionSelector } from '../../../shared/stores/chatSessionStore';
import { selectSession, removeSession } from '../../../shared/stores/chatSessionSlice';
import { ChatSessionService } from '../../../data/services/ChatSessionService';
import { loadChatSessions } from '../../../shared/hooks/useLoadChatSessions';
import { useUserSelector } from '../../../shared/stores/userStore';
import { useTitleUpdateListener } from '../../../shared/hooks/useTitleUpdateListener';
import { ROUTES, getChatSessionRoute } from '../../../shared/utils';
import { UiButton, UiIconButton } from '../../../shared/components/ui';
import { designTokens } from '../../../design_system/colors';
import { useSettingsSelector, useSettingsDispatch } from '../../../features/settings/stores/settingsStore.ts';
import { loadSavedProviders } from '../../../features/settings/stores/modelProviderSlice.ts';

interface NavigationDrawerProps {
  isOpen: boolean;
  onToggle: () => void;
  onClose: () => void;
}

const DRAWER_WIDTH = 240;

const navigationItems = [
  { text: 'Home', icon: <HomeIcon />, path: ROUTES.HOME },
];

const bottomNavigationItems = [
  { text: 'Settings', icon: <SettingsIcon />, path: ROUTES.SETTINGS },
];

/**
 * NavigationDrawer Component
 */
const NavigationDrawer = ({ isOpen, onToggle, onClose }: NavigationDrawerProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const tokens = designTokens[theme.palette.mode === 'dark' ? 'dark' : 'light'];
  const isLargeScreen = useMediaQuery(theme.breakpoints.up('lg'));

  const [showSettingsView, setShowSettingsView] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useTitleUpdateListener();

  const chatSessionDispatch = useChatSessionDispatch();
  const {
    sessions,
    loading: sessionsLoading,
    selectedSessionId,
    creatingSession
  } = useChatSessionSelector(state => state.chatSession);
  const { userId } = useUserSelector(state => state.user);

  // Primary model from settings store
  const settingsDispatch = useSettingsDispatch();
  const savedProviders = useSettingsSelector(state => state.modelProvider.savedProviders);

  // Debug: log full savedProviders to understand API response shape
  useEffect(() => {
    console.log('[NavDrawer] savedProviders:', JSON.stringify(savedProviders, null, 2));
  }, [savedProviders]);

  // Find primary provider: explicitly marked as primary, then any provider with a selected model
  const primaryProvider = savedProviders.find(p => p.is_primary);
  const selectedModelName = primaryProvider?.selected_model ?? null;
  const providerName = primaryProvider?.provider_name ?? null;

  // Load saved providers on mount and refresh when navigating back from settings
  useEffect(() => {
    settingsDispatch(loadSavedProviders());
  }, [location.pathname, settingsDispatch]);

  const filteredSessions = searchQuery.trim()
    ? sessions.filter(s => (s.title || '').toLowerCase().includes(searchQuery.toLowerCase()))
    : sessions;

  const handleNavigate = (path: string) => {
    navigate(path);
    if (!isLargeScreen) onClose();
  };

  const handleHomeClick = () => {
    setShowSettingsView(false);
    handleNavigate(ROUTES.HOME);
  };

  const handleSettingsClick = () => {
    if (!showSettingsView) {
      setShowSettingsView(true);
      handleNavigate(ROUTES.SETTINGS_GENERAL);
    } else {
      setShowSettingsView(false);
    }
  };

  const handleSettingsItemSelect = (path: string) => {
    handleNavigate(path);
  };

  const handleCreateNewChat = async () => {
    setShowSettingsView(false);
    handleNavigate(ROUTES.CHAT);
  };

  const handleSelectSession = (sessionId: string) => {
    setShowSettingsView(false);
    chatSessionDispatch(selectSession(sessionId));
    handleNavigate(getChatSessionRoute(sessionId));
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      const service = new ChatSessionService();
      await service.deleteSession(sessionId);
      chatSessionDispatch(removeSession(sessionId));
      if (userId) chatSessionDispatch(loadChatSessions(userId));
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const drawerContent = (
    <Box
      sx={{
        width: DRAWER_WIDTH,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: tokens.background.sidebar,
      }}
    >
      {/* ── Header ── */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 2,
          py: 1.75,
          minHeight: 72,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25, 
              cursor: 'pointer', }} onClick={handleHomeClick}>
          <Box
            
            sx={{
              width: 38,
              height: 38,
              borderRadius: '12px',
              background: `linear-gradient(135deg, ${tokens.accent.primary}, ${tokens.accent.primaryHover})`,
              flexShrink: 0,
            }}
          />
          <Typography variant="h3" sx={{ fontWeight: 700 }} >
            Personal AI
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.25 }}>
          <UiIconButton tone="ghost" size="small" sx={{ width: 34, height: 34 }} onClick={onToggle}>
            {isOpen ? <ChevronLeftIcon sx={{ fontSize: 18 }} /> : <MenuIcon sx={{ fontSize: 18 }} />}
          </UiIconButton>
        </Box>
      </Box>

      {/* ── New Chat Button ── */}
      <Box sx={{ px: 1.5, pb: 1.25 }}>
        <UiButton
          fullWidth
          startIcon={creatingSession ? <CircularProgress size={16} color="inherit" /> : <AddIcon />}
          onClick={handleCreateNewChat}
          disabled={creatingSession || !userId}
          sx={{ borderRadius: '12px', minHeight: 42 }}
        >
          {creatingSession ? 'Creating...' : 'New Chat'}
        </UiButton>
      </Box>

      {/* ── Search Input ── */}
      <Box sx={{ px: 1.5, pb: 1 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.75,
            px: 1.5,
            py: 0.75,
            borderRadius: '12px',
            border: `1px solid ${tokens.border.subtle}`,
            backgroundColor: tokens.surface.tertiary,
          }}
        >
          <SearchIcon sx={{ fontSize: 18, color: tokens.text.muted, flexShrink: 0 }} />
          <InputBase
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{
              flex: 1,
              fontSize: '0.82rem',
              color: tokens.text.primary,
              '& input::placeholder': { color: tokens.text.muted },
            }}
          />
        </Box>
      </Box>

      <Divider sx={{ borderColor: tokens.border.subtle }} />

      {/* ── Conditional Content: Sessions or Settings ── */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {!showSettingsView ? (
          <Box sx={{ px: 1.5, py: 1.25 }}>
            <Typography
              variant="overline"
              sx={{ color: 'text.secondary', fontWeight: 700, display: 'block', mb: 0.75, px: 0.5, fontSize: '0.65rem', letterSpacing: '0.1em' }}
            >
              RECENT
            </Typography>
            <ChatSessionList
              sessions={filteredSessions}
              sessionsLoading={sessionsLoading}
              selectedSessionId={selectedSessionId}
              onSelectSession={handleSelectSession}
              onDeleteSession={handleDeleteSession}
            />
          </Box>
        ) : (
          <SettingsItemList
            onSelectItem={handleSettingsItemSelect}
            selectedPath={location.pathname}
          />
        )}
      </Box>

      {/* ── Bottom: Settings nav + Home ── */}
      <Divider sx={{ borderColor: tokens.border.subtle }} />
      <List sx={{ py: 0.5 }}>
        {navigationItems.map((item) => (
          <NavigationItem
            key={item.text}
            text={item.text}
            icon={item.icon}
            isSelected={!showSettingsView && location.pathname === item.path}
            onClick={handleHomeClick}
          />
        ))}
        {bottomNavigationItems.map((item) => (
          <NavigationItem
            key={item.text}
            text={item.text}
            icon={item.icon}
            isSelected={showSettingsView}
            onClick={handleSettingsClick}
          />
        ))}
      </List>

      {/* ── Model Selector ── */}
      <Box sx={{ px: 1.5, pb: 1.5, pt: 0.5 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            px: 1.25,
            py: 1,
            borderRadius: '12px',
            border: `1px solid ${tokens.border.subtle}`,
            backgroundColor: tokens.surface.tertiary,
            cursor: 'pointer',
            transition: 'background-color 150ms',
            '&:hover': { backgroundColor: alpha(tokens.accent.primary, 0.06) },
          }}
          onClick={() => handleNavigate(ROUTES.SETTINGS_MODELS)}
        >
          <Box
            sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: selectedModelName ? tokens.status.success : tokens.status.warning, flexShrink: 0 }}
          />
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="caption" sx={{ fontWeight: 700, display: 'block', lineHeight: 1.3 }} noWrap>
              {selectedModelName ? providerName : 'Select Model'}
            </Typography>
            {selectedModelName && (
              <Typography sx={{ fontSize: '0.65rem', color: 'text.secondary', lineHeight: 1.2 }} noWrap>
                {selectedModelName}
              </Typography>
            )}
          </Box>
          <ExpandMoreIcon sx={{ fontSize: 18, color: 'text.secondary', flexShrink: 0 }} />
        </Box>
      </Box>
    </Box>
  );

  if (isLargeScreen) {
    return (
      <Drawer
        variant="permanent"
        open={isOpen}
        sx={{
          width: isOpen ? DRAWER_WIDTH : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            backgroundColor: tokens.background.sidebar,
            borderRight: `1px solid ${tokens.border.subtle}`,
            transform: isOpen ? 'translateX(0)' : `translateX(-${DRAWER_WIDTH}px)`,
            transition: theme.transitions.create(['transform'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          },
        }}
      >
        {drawerContent}
      </Drawer>
    );
  }

  return (
    <Drawer
      variant="temporary"
      open={isOpen}
      onClose={onClose}
      ModalProps={{ keepMounted: true }}
      sx={{
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          backgroundColor: tokens.background.sidebar,
          borderRight: `1px solid ${tokens.border.subtle}`,
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export { NavigationDrawer, DRAWER_WIDTH };
