import { Box, CircularProgress, InputBase, Typography } from '@mui/material';
import {
  AttachFile as AttachFileIcon,
  Forum as ForumIcon,
  SmartToy as SmartToyIcon,
} from '@mui/icons-material';
import { alpha, useTheme } from '@mui/material/styles';
import { useState, type FormEvent, useRef } from 'react';
import { ChatModeType } from '../types/chatMessage.types';
import type { FileData } from '../types/fileUpload.types';
import { ACCEPTED_FILE_TYPES } from '../../../util/FileUtil.ts';
import { designTokens, fontWeight, fontSize } from '../../../design_system/colors';
import { useSettingsSelector } from '../../../features/settings/stores/settingsStore.ts';

interface ChatFooterProps {
  onSendMessage: (message: string, chatMode: ChatModeType) => void;
  disabled?: boolean;
  sending?: boolean;
  chatMode?: ChatModeType;
  onChatModeChange?: (mode: ChatModeType) => void;
  onFileSelect?: (files: Array<FileData & { file?: File }>) => void;
}

/** Normalise legacy OFFLINE → CHAT */
const normaliseMode = (m: ChatModeType): ChatModeType =>
  m === ChatModeType.OFFLINE ? ChatModeType.CHAT : m;

export const ChatFooter = ({
  onSendMessage,
  disabled = false,
  sending = false,
  chatMode: initialChatMode = ChatModeType.CHAT,
  onChatModeChange,
  onFileSelect,
}: ChatFooterProps) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const tokens = designTokens[isDark ? 'dark' : 'light'];

  const [message, setMessage] = useState('');
  const [chatMode, setChatMode] = useState<ChatModeType>(normaliseMode(initialChatMode));
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isAgent = chatMode === ChatModeType.AGENT;

  // Selected model from settings store
  const savedProviders = useSettingsSelector(state => state.modelProvider.savedProviders);
  const primaryProvider = savedProviders.find(p => p.is_primary) ?? savedProviders[0] ?? null;
  const selectedModelName = primaryProvider?.selected_model ?? null;

  /** Teal for Chat, amber for Agent */
  const modeColor = isAgent ? tokens.accent.secondary : tokens.accent.primary;
  const modeHover = isAgent ? tokens.accent.secondaryHover : tokens.accent.primaryHover;
  const modeAlpha = (a: number) => alpha(modeColor, a);

  // ── Handlers ──────────────────────────────────────────────────────────
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled && !sending) {
      onSendMessage(message.trim(), chatMode);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  };

  const handleToggleMode = () => {
    const next = isAgent ? ChatModeType.CHAT : ChatModeType.AGENT;
    setChatMode(next);
    onChatModeChange?.(next);
  };

  const handleFileButtonClick = () => fileInputRef.current?.click();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0 && onFileSelect) {
      onFileSelect(
        Array.from(files).map((file) => ({
          name: file.name,
          size: file.size,
          type: file.type,
          lastModified: file.lastModified,
          preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
          file,
        })),
      );
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const canSend = message.trim().length > 0 && !disabled && !sending;

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        px: { xs: 1.5, md: 2 },
        pt: 1.5,
        pb: 1.5,
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        backgroundColor: 'transparent',
      }}
    >
      {/* ══════════════════════════════════════════════════════════════════
          Single bordered container: [📎 | input ... | Send | toggle]
      ══════════════════════════════════════════════════════════════════ */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 0,
          px: 1.5,
          py: 0.75,
          borderRadius: '14px',
          border: `1.5px solid ${tokens.border.subtle}`,
          backgroundColor: tokens.surface.primary,
          transition: 'border-color 180ms, box-shadow 180ms',
          '&:focus-within': {
            borderColor: modeColor,
            boxShadow: `0 0 0 3px ${modeAlpha(0.1)}`,
          },
        }}
      >
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={ACCEPTED_FILE_TYPES}
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />

        {/* Attach button */}
        <Box
          component="button"
          type="button"
          onClick={handleFileButtonClick}
          disabled={disabled || sending}
          sx={{
            p: 0.5,
            mr: 0.5,
            border: 'none',
            background: 'transparent',
            cursor: disabled || sending ? 'not-allowed' : 'pointer',
            color: tokens.text.muted,
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            flexShrink: 0,
            opacity: disabled || sending ? 0.45 : 1,
            transition: 'color 150ms',
            '&:hover:not(:disabled)': { color: tokens.text.secondary },
          }}
        >
          <AttachFileIcon sx={{ fontSize: 18 }} />
        </Box>

        {/* Text input — takes all remaining space */}
        <InputBase
          multiline
          maxRows={5}
          fullWidth
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || sending}
          sx={{
            flex: 1,
            fontSize: fontSize.base,
            fontWeight: fontWeight.regular,
            lineHeight: 1.55,
            color: tokens.text.primary,
            '& textarea::placeholder': { color: tokens.text.muted, opacity: 1 },
            '& .MuiInputBase-input': { py: 0.5 },
          }}
        />

        {/* ── Split send pill: [Send][▏][icon]  — one connected pill ── */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'stretch',
            borderRadius: '999px',
            overflow: 'hidden',
            ml: 1,
            flexShrink: 0,
            minHeight: 40,
            boxShadow: canSend ? `0 2px 12px ${modeAlpha(0.38)}` : 'none',
            transition: 'box-shadow 200ms',
          }}
        >
          {/* Send half — greyed when disabled/empty */}
          <Box
            component="button"
            type="submit"
            disabled={!canSend}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              pl: 1.8,
              pr: 1.5,
              border: 'none',
              borderRadius: 0,
              fontFamily: 'inherit',
              fontSize: fontSize.md,
              fontWeight: fontWeight.semibold,
              background: canSend ? modeColor : alpha(tokens.text.muted, 0.13),
              color: canSend ? '#ffffff' : tokens.text.muted,
              cursor: canSend ? 'pointer' : 'not-allowed',
              transition: 'background 180ms',
              '&:hover:not(:disabled)': {
                background: canSend ? modeHover : undefined,
              },
            }}
          >
            {sending ? (
              <CircularProgress size={13} sx={{ color: 'inherit' }} />
            ) : null}
            <Typography
              component="span"
              sx={{ fontSize: 'inherit', fontWeight: 'inherit', lineHeight: 1 }}
            >
              Send
            </Typography>
          </Box>

          {/* White-alpha divider */}
          <Box
            sx={{
              width: '1px',
              background: canSend ? alpha('#ffffff', 0.28) : alpha(tokens.text.muted, 0.18),
              flexShrink: 0,
            }}
          />

          {/* Toggle half — ALWAYS shows mode colour, never disabled */}
          <Box
            component="button"
            type="button"
            onClick={handleToggleMode}
            title={`Switch to ${isAgent ? 'Chat' : 'Agent'} mode`}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              px: 1.25,
              border: 'none',
              borderRadius: 0,
              cursor: 'pointer',
              background: isAgent ? tokens.accent.secondaryActive : tokens.accent.primaryActive,
              color: '#ffffff',
              transition: 'background 180ms, opacity 150ms',
              '&:hover': { opacity: 0.82 },
            }}
          >
            {isAgent ? (
              <SmartToyIcon sx={{ fontSize: 16 }} />
            ) : (
              <ForumIcon sx={{ fontSize: 16 }} />
            )}
          </Box>
        </Box>
      </Box>

      {/* ── Status row — right-aligned ──────────────────────────────── */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 0.75,
          px: 0.5,
        }}
      >
        {/* Left: context description */}
        <Typography
          sx={{
            fontSize: fontSize.xs,
            fontWeight: fontWeight.regular,
            color: tokens.text.muted,
            lineHeight: 1,
          }}
        >
          {isAgent ? 'Web search enabled' : 'Direct LLM conversation'}
        </Typography>

        {/* Right: Sending as + chips */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
        <Typography
          sx={{
            fontSize: fontSize.xs,
            fontWeight: fontWeight.medium,
            color: tokens.text.muted,
            lineHeight: 1,
          }}
        >
          Sending as
        </Typography>

        {/* Combined pill: [ icon Mode | GPT-4o ] — one connected pill, click to toggle */}
        <Box
          onClick={handleToggleMode}
          sx={{
            display: 'flex',
            alignItems: 'stretch',
            borderRadius: '999px',
            overflow: 'hidden',
            border: `1px solid ${modeAlpha(0.3)}`,
            cursor: 'pointer',
            transition: 'border-color 160ms',
            '&:hover': { borderColor: modeAlpha(0.5) },
          }}
        >
          {/* Mode half — coloured tint */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.4,
              px: 0.9,
              py: 0.4,
              backgroundColor: modeAlpha(isDark ? 0.18 : 0.1),
            }}
          >
            {isAgent ? (
              <SmartToyIcon sx={{ fontSize: 11, color: modeColor }} />
            ) : (
              <ForumIcon sx={{ fontSize: 11, color: modeColor }} />
            )}
            <Typography
              sx={{
                fontSize: fontSize.xs,
                fontWeight: fontWeight.semibold,
                color: modeColor,
                lineHeight: 1,
              }}
            >
              {isAgent ? 'Agent' : 'Chat'}
            </Typography>
          </Box>

          {/* Internal divider */}
          <Box sx={{ width: '1px', backgroundColor: modeAlpha(0.25), flexShrink: 0 }} />

          {/* GPT-4o half — same mode tint */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              px: 0.9,
              py: 0.4,
              backgroundColor: modeAlpha(isDark ? 0.18 : 0.1),
            }}
          >
            <Typography
              sx={{
                fontSize: fontSize.xs,
                fontWeight: fontWeight.medium,
                color: modeColor,
                lineHeight: 1,
              }}
            >
              {selectedModelName ?? 'Select Model'}
            </Typography>
          </Box>
        </Box>

        </Box> {/* end right chips group */}
      </Box>
    </Box>
  );
};
