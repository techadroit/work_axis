import { useState } from 'react';
import { Box, InputBase, Typography } from '@mui/material';
import {
  AutoAwesomeOutlined,
  Code as CodeIcon,
  EditOutlined,
  PublicOutlined,
  LightbulbOutlined,
  NorthEast as NorthEastIcon,
  ForumOutlined,
  SmartToyOutlined,
  Close as CloseIcon,
  Menu as MenuIcon,
} from '@mui/icons-material';
import { alpha, useTheme } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import { useOutletContext } from 'react-router-dom';
import { UiButton, UiIconButton } from '../../../shared/components/ui';
import { ROUTES } from '../../../shared/utils';
import { designTokens } from '../../../design_system/colors';
import { ChatModeType } from '../../chat/types/chatMessage.types';

const getGreeting = () => {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
};

const promptCards = [
  {
    category: 'CODING',
    Icon: CodeIcon,
    color: '#2563EB',
    text: 'Help me debug this Python function that keeps returning None',
    highlighted: false,
    mode: ChatModeType.CHAT,
  },
  {
    category: 'WRITING',
    Icon: EditOutlined,
    color: '#2563EB',
    text: 'Write a professional email to decline a meeting politely',
    highlighted: false,
    mode: ChatModeType.CHAT,
  },
  {
    category: 'WEB SEARCH',
    Icon: PublicOutlined,
    color: '#2563EB',
    text: 'What are the latest updates on React 19 features?',
    highlighted: true,
    mode: ChatModeType.AGENT,
  },
  {
    category: 'IDEAS',
    Icon: LightbulbOutlined,
    color: '#2563EB',
    text: 'Brainstorm 5 creative names for my new startup',
    highlighted: false,
    mode: ChatModeType.AGENT,
  },
];


export const HomeLanding = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const tokens = designTokens[theme.palette.mode === 'dark' ? 'dark' : 'light'];
  const [showProTip, setShowProTip] = useState(true);

  const { toggleDrawer, isLargeScreen, isConnected, connectionLabel } =
    useOutletContext<{ toggleDrawer: () => void; isLargeScreen: boolean; isConnected: boolean; connectionLabel: string }>();

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Small-screen header with hamburger */}
      {!isLargeScreen && (
        <Box
          sx={{
            px: 1.5,
            py: 1,
            borderBottom: `1px solid ${tokens.border.subtle}`,
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
          <Typography variant="h6" sx={{ flex: 1, fontWeight: 600 }}>Home</Typography>
          <Box
            sx={{
              px: 1.25, py: 0.6, borderRadius: '999px',
              border: `1px solid ${tokens.border.subtle}`,
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
          p: { xs: 2, md: 3, lg: 4 },
          display: 'flex',
          flexDirection: 'column',
          gap: { xs: 2.5, md: 3 },
        '@keyframes fadeSlide': {
          from: { opacity: 0, transform: 'translateY(10px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
      }}
    >
      {/* ── Greeting ── */}
      <Box sx={{ animation: 'fadeSlide 260ms ease-out' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 0.5, flexWrap: 'wrap' }}>
          <Typography
            variant="h3"
            sx={{ fontWeight: 700, color: 'text.primary', lineHeight: 1.1, letterSpacing: '-0.02em' }}
          >
            {getGreeting()}
          </Typography>
          <Typography sx={{ fontSize: '2rem', lineHeight: 1 }}>👋</Typography>
        </Box>
        <Typography variant="body1" color="text.secondary">
          What would you like to explore today? Start a conversation or try one of the suggestions below.
        </Typography>
      </Box>

      {/* ── Prompt Input Bar ── */}
      <Box
        onClick={() => navigate(ROUTES.CHAT)}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          px: 2,
          py: 0.75,
          borderRadius: '16px',
          border: `1.5px solid ${tokens.border.subtle}`,
          backgroundColor: tokens.surface.primary,
          boxShadow: tokens.shadow.soft,
          cursor: 'pointer',
          transition: 'border-color 180ms, box-shadow 180ms',
          '&:hover': {
            borderColor: tokens.accent.primary,
            boxShadow: `0 0 0 4px ${alpha(tokens.accent.primary, 0.1)}`,
          },
        }}
      >
        <AutoAwesomeOutlined sx={{ color: tokens.accent.primary, fontSize: 22, flexShrink: 0 }} />
        <InputBase
          readOnly
          placeholder="Ask me anything or start with a suggestion below..."
          sx={{
            flex: 1,
            fontSize: '0.95rem',
            color: tokens.text.muted,
            pointerEvents: 'none',
            '& input': { cursor: 'pointer' },
          }}
        />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, flexShrink: 0 }}>
          {['Chat', 'Agent'].map((mode) => (
            <Box
              key={mode}
              sx={{
                px: 1.5,
                py: 0.5,
                borderRadius: '999px',
                border: `1.5px solid ${tokens.border.subtle}`,
                fontSize: '0.78rem',
                fontWeight: 600,
                color: tokens.text.secondary,
                backgroundColor: tokens.surface.tertiary,
              }}
            >
              {mode}
            </Box>
          ))}
          <Box
            sx={{
              width: 36,
              height: 36,
              borderRadius: '10px',
              background: `linear-gradient(135deg, ${tokens.accent.primary}, ${tokens.accent.primaryHover})`,
              display: 'grid',
              placeItems: 'center',
              color: tokens.text.inverse,
            }}
          >
            <NorthEastIcon sx={{ fontSize: 18 }} />
          </Box>
        </Box>
      </Box>

      {/* ── Try These Prompts ── */}
      <Box sx={{ animation: 'fadeSlide 320ms ease-out' }}>
        <Typography
          variant="overline"
          sx={{ color: 'text.secondary', fontWeight: 700, display: 'block', mb: 1.5, letterSpacing: '0.1em' }}
        >
          TRY THESE PROMPTS
        </Typography>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr 1fr', lg: 'repeat(4, minmax(0, 1fr))' },
            gap: 1.5,
          }}
        >
          {promptCards.map((card) => {
            const isAgent = card.mode === ChatModeType.AGENT;
            const modeColor = isAgent ? tokens.accent.secondary : tokens.accent.primary;
            return (
              <Box
                key={card.category}
                onClick={() => navigate(ROUTES.CHAT, { state: { chatMode: card.mode } })}
                sx={{
                  p: 2,
                  borderRadius: '14px',
                  border: `1px solid ${tokens.border.subtle}`,
                  backgroundColor: tokens.surface.primary,
                  cursor: 'pointer',
                  transition: 'transform 150ms, box-shadow 150ms',
                  '&:hover': { transform: 'translateY(-2px)', boxShadow: tokens.shadow.medium },
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, mb: 1 }}>
                  <card.Icon sx={{ fontSize: 15, color: card.color }} />
                  <Typography
                    variant="overline"
                    sx={{ color: card.color, fontWeight: 700, lineHeight: 1, fontSize: '0.62rem', letterSpacing: '0.08em', flex: 1 }}
                  >
                    {card.category}
                  </Typography>
                  <Box
                    sx={{
                      px: 0.75,
                      py: 0.25,
                      borderRadius: '999px',
                      backgroundColor: alpha(modeColor, 0.12),
                      border: `1px solid ${alpha(modeColor, 0.28)}`,
                      fontSize: '0.58rem',
                      fontWeight: 700,
                      color: modeColor,
                      lineHeight: 1.4,
                      letterSpacing: '0.04em',
                      textTransform: 'uppercase',
                      flexShrink: 0,
                    }}
                  >
                    {isAgent ? 'Agent' : 'Chat'}
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ color: 'text.primary', lineHeight: 1.55, fontSize: '0.875rem' }}>
                  {card.text}
                </Typography>
              </Box>
            );
          })}
        </Box>
      </Box>

      {/* ── Chat / Agent Mode Cards ── */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          gap: 1.5,
          animation: 'fadeSlide 360ms ease-out',
        }}
      >
        {/* Chat Mode */}
        <Box
          sx={{
            p: 3,
            borderRadius: '16px',
            border: `1.5px solid ${alpha(tokens.accent.primary, 0.28)}`,
            backgroundColor: alpha(tokens.accent.primary, 0.05),
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
            <Box
              sx={{
                width: 52,
                height: 52,
                borderRadius: '16px',
                background: `linear-gradient(135deg, ${tokens.accent.primary}, ${tokens.accent.primaryHover})`,
                display: 'grid',
                placeItems: 'center',
                flexShrink: 0,
              }}
            >
              <ForumOutlined sx={{ color: tokens.text.inverse, fontSize: 24 }} />
            </Box>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, lineHeight: 1.3 }}>
                Chat Mode
              </Typography>
              <Typography variant="caption" sx={{ color: tokens.accent.primary, fontWeight: 600 }}>
                Direct LLM conversation
              </Typography>
            </Box>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5, lineHeight: 1.65 }}>
            Have focused conversations with your configured LLM. Perfect for creative writing, coding assistance,
            brainstorming, and general questions.
          </Typography>
          <UiButton onClick={() => navigate(ROUTES.CHAT, { state: { chatMode: ChatModeType.CHAT } })} sx={{ borderRadius: '10px', minHeight: 42 }}>
            Start Chat
          </UiButton>
        </Box>

        {/* Agent Mode */}
        <Box
          sx={{
            p: 3,
            borderRadius: '16px',
            border: `1.5px solid ${alpha(tokens.accent.secondary, 0.38)}`,
            backgroundColor: alpha(tokens.accent.secondary, 0.07),
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
            <Box
              sx={{
                width: 52,
                height: 52,
                borderRadius: '16px',
                background: `linear-gradient(135deg, ${tokens.accent.secondary}, ${tokens.accent.secondaryHover})`,
                display: 'grid',
                placeItems: 'center',
                flexShrink: 0,
              }}
            >
              <SmartToyOutlined sx={{ color: '#fff', fontSize: 24 }} />
            </Box>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, lineHeight: 1.3 }}>
                Agent Mode
              </Typography>
              <Typography variant="caption" sx={{ color: tokens.accent.secondary, fontWeight: 600 }}>
                Web search enabled
              </Typography>
            </Box>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5, lineHeight: 1.65 }}>
            Get answers powered by real-time web search. Ideal for current events, research, fact-checking, and
            finding the latest information.
          </Typography>
          <Box
            component="button"
            onClick={() => navigate(ROUTES.CHAT,{ state: { chatMode: ChatModeType.AGENT } })}
            sx={{
              px: 3,
              py: 1.1,
              minHeight: 42,
              borderRadius: '10px',
              border: 'none',
              background: `linear-gradient(135deg, ${tokens.accent.secondary}, ${tokens.accent.secondaryHover})`,
              color: '#fff',
              fontWeight: 700,
              fontSize: '0.9rem',
              fontFamily: 'inherit',
              cursor: 'pointer',
              transition: 'opacity 150ms',
              '&:hover': { opacity: 0.88 },
            }}
          >
            Start Agent
          </Box>
        </Box>
      </Box>



      {/* ── Pro Tip Banner ── */}
      {showProTip && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            p: 2,
            borderRadius: '14px',
            backgroundColor: alpha(tokens.accent.primary, 0.06),
            border: `1px solid ${alpha(tokens.accent.primary, 0.18)}`,
            animation: 'fadeSlide 440ms ease-out',
          }}
        >
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: '12px',
              background: `linear-gradient(135deg, ${tokens.accent.primary}, ${tokens.accent.primaryHover})`,
              display: 'grid',
              placeItems: 'center',
              flexShrink: 0,
            }}
          >
            <LightbulbOutlined sx={{ color: tokens.text.inverse, fontSize: 20 }} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
              Pro Tip
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Use Agent mode for questions about recent events — it searches the web for up-to-date information!
            </Typography>
          </Box>
          <UiIconButton tone="ghost" size="small" onClick={() => setShowProTip(false)} sx={{ width: 32, height: 32 }}>
            <CloseIcon sx={{ fontSize: 16 }} />
          </UiIconButton>
        </Box>
      )}
    </Box>
    </Box>
  );
};
