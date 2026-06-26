import {Box, IconButton, useTheme} from '@mui/material';
import {Outlet, useLocation} from 'react-router-dom';
import {useEffect} from 'react';
import { Menu as MenuIcon } from '@mui/icons-material';
import {useDrawer} from "../../features/navigation_drawer/hooks/useDrawer";
import {NavigationDrawer} from "../../features/navigation_drawer/components/navigation-drawer.tsx";
import {loadUser} from '../hooks/useLoadUser';
import {useUserDispatch, useUserSelector} from "../stores/userStore.ts";
import {useChatSessionDispatch, useChatSessionSelector} from "../stores/chatSessionStore.ts";
import {loadChatSessions} from "../hooks/useLoadChatSessions.ts";
import {useWebSocketConnection} from "../hooks/useWebSocketConnection.ts";
import {useGlobalWebSocketListener} from "../hooks/useGlobalWebSocketListener.ts";
import { useSettingsDispatch } from '../../features/settings/stores/settingsStore.ts';
import { loadSavedProviders } from '../../features/settings/stores/modelProviderSlice.ts';

/**
 * MainScreen - The primary container component that renders when the app launches
 * Contains all routes and serves as the root layout component with navigation drawer
 */
const MainScreen = () => {
    const {isOpen, isLargeScreen, toggleDrawer} = useDrawer();
    const theme = useTheme();
    const location = useLocation();
    const userDispatch = useUserDispatch();
    const chatSessionDispatch = useChatSessionDispatch();
    const settingsDispatch = useSettingsDispatch();

    const chatSessionState = useChatSessionSelector(state => state.chatSession)
    // Get the entire user state for debugging
    const {userId, loading} = useUserSelector(state => state.user);

    // Initialize WebSocket connection when user is loaded
    const { connectionState, isConnected } = useWebSocketConnection();

    // Initialize global WebSocket message router
    useGlobalWebSocketListener();

    // Load user on mount
    useEffect(() => {
        if (!loading && !userId) {
            userDispatch(loadUser());
        }
    }, [userDispatch, userId, loading]);

    // Load chat sessions when user is loaded
    useEffect(() => {
        if (userId) {
            chatSessionDispatch(loadChatSessions(userId));
        }
    }, [chatSessionDispatch, userId]);

    // Load saved model providers on mount (used by drawer + ChatFooter)
    useEffect(() => {
        settingsDispatch(loadSavedProviders());
    }, [settingsDispatch]);

    useEffect(() => {
        console.log("MainScreen - chatSessionState State:", chatSessionState);
    }, [chatSessionState]);

    useEffect(() => {
        console.log("MainScreen - WebSocket State:", connectionState, "Connected:", isConnected);
    }, [connectionState, isConnected]);

    const sectionTitle = location.pathname.startsWith('/settings')
        ? 'Settings'
        : location.pathname.startsWith('/chat')
            ? 'Chat'
            : 'Workspace';

    const connectionLabel = isConnected ? 'Connected' : 'Offline';

    return (
        <Box
            sx={{
                display: 'flex',
                minHeight: '100vh',
            }}
        >
            {/* Navigation Drawer */}
            <NavigationDrawer
                isOpen={isOpen}
                onToggle={toggleDrawer}
                onClose={toggleDrawer}
            />

            {/* Main Content Area */}
            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    height: '100vh',
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column',
                    transition: theme.transitions.create(['margin'], {
                        easing: theme.transitions.easing.sharp,
                        duration: theme.transitions.duration.enteringScreen,
                    }),
                    marginLeft: isLargeScreen && isOpen ? 0 : 0,
                }}
            >
                {/* Outlet renders the matched child route.
                    Context carries drawer controls so child screens can embed
                    the hamburger inside their own header on small screens. */}
                <Box sx={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    overflow: 'hidden',
                    minHeight: 0,
                    position: 'relative',
                }}>
                    {/* Floating re-open toggle — only on large screens when drawer is collapsed */}
                    {isLargeScreen && !isOpen && (
                        <IconButton
                            onClick={toggleDrawer}
                            size="small"
                            aria-label="open navigation"
                            sx={{
                                position: 'absolute',
                                top: 12,
                                left: 12,
                                zIndex: 10,
                                bgcolor: 'background.paper',
                                border: '1px solid var(--border-subtle)',
                                borderRadius: '10px',
                                width: 36,
                                height: 36,
                                boxShadow: 1,
                                '&:hover': { bgcolor: 'action.hover' },
                            }}
                        >
                            <MenuIcon fontSize="small" />
                        </IconButton>
                    )}
                    <Outlet context={{ toggleDrawer, isConnected, isLargeScreen, connectionLabel, sectionTitle }} />
                </Box>
            </Box>
        </Box>
    );
};

export default MainScreen;

