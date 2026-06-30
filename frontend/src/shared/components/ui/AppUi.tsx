import type { ReactNode } from 'react';
import {
  Avatar,
  Box,
  Button,
  Divider,
  IconButton,
  Paper,
  Skeleton,
  TextField,
  Typography,
  type AvatarProps,
  type BoxProps,
  type ButtonProps,
  type DividerProps,
  type IconButtonProps,
  type PaperProps,
  type TextFieldProps,
  type TypographyProps,
} from '@mui/material';
import { alpha, type SxProps, type Theme } from '@mui/material/styles';
import { PersonRounded, SmartToyOutlined } from '@mui/icons-material';
import { designTokens } from '../../../design_system/colors';

type UiButtonTone = 'primary' | 'secondary' | 'ghost';
type UiIconTone = 'primary' | 'neutral' | 'ghost';

const mergeSx = (base: SxProps<Theme>, sx?: SxProps<Theme>): SxProps<Theme> => [base, sx] as SxProps<Theme>;
const resolveTokens = (theme: Theme) => designTokens[theme.palette.mode === 'dark' ? 'dark' : 'light'];

export const UiPanel = ({ sx, children, ...props }: PaperProps) => (
  <Paper
    elevation={0}
    {...props}
    sx={mergeSx(
      (theme) => {
        const tokens = resolveTokens(theme);

        return {
          backgroundColor: tokens.surface.primary,
          border: `1px solid ${tokens.border.subtle}`,
          borderRadius: `${tokens.radius.lg}px`,
          boxShadow: tokens.shadow.soft,
          backdropFilter: 'blur(18px)',
        };
      },
      sx,
    )}
  >
    {children}
  </Paper>
);

interface UiSectionTitleProps extends TypographyProps {
  eyebrow?: string;
  detail?: string;
}

export const UiSectionTitle = ({
  eyebrow,
  detail,
  children,
  sx,
  ...props
}: UiSectionTitleProps) => (
  <Box>
    {eyebrow && (
      <Typography
        variant="overline"
        sx={{
          color: 'text.secondary',
          display: 'block',
          mb: 0.5,
        }}
      >
        {eyebrow}
      </Typography>
    )}
    <Typography
      variant="h6"
      {...props}
      sx={mergeSx(
        {
          color: 'text.primary',
          fontWeight: 700,
        },
        sx,
      )}
    >
      {children}
    </Typography>
    {detail && (
      <Typography
        variant="body2"
        sx={{
          color: 'text.secondary',
          mt: 0.5,
        }}
      >
        {detail}
      </Typography>
    )}
  </Box>
);

interface UiDividerProps extends DividerProps {
  insetX?: number | string | Record<string, number | string>;
}

export const UiDivider = ({ insetX, sx, ...props }: UiDividerProps) => (
  <Divider
    {...props}
    sx={mergeSx(
      (theme) => {
        const tokens = resolveTokens(theme);

        return {
          borderColor: tokens.border.subtle,
          ...(insetX !== undefined ? { mx: insetX } : {}),
        };
      },
      sx,
    )}
  />
);

interface UiButtonProps extends ButtonProps {
  tone?: UiButtonTone;
}

export const UiButton = ({ tone = 'primary', sx, children, variant, ...props }: UiButtonProps) => (
  <Button
    variant={variant ?? (tone === 'ghost' ? 'text' : 'contained')}
    {...props}
    sx={mergeSx(
      (theme) => {
        const tokens = resolveTokens(theme);
        const primaryStyles = {
          background: `linear-gradient(135deg, ${tokens.accent.primary}, ${tokens.accent.primaryHover})`,
          color: tokens.text.inverse,
          border: 'none',
          '&:hover': {
            background: `linear-gradient(135deg, ${tokens.accent.primaryHover}, ${tokens.accent.primaryActive})`,
          },
        };

        const secondaryStyles = {
          backgroundColor: alpha(tokens.accent.secondary, theme.palette.mode === 'light' ? 0.18 : 0.22),
          color: tokens.text.primary,
          border: `1px solid ${alpha(tokens.accent.secondary, 0.34)}`,
          '&:hover': {
            backgroundColor: alpha(tokens.accent.secondary, theme.palette.mode === 'light' ? 0.28 : 0.3),
            borderColor: alpha(tokens.accent.secondary, 0.46),
          },
        };

        const ghostStyles = {
          backgroundColor: 'transparent',
          color: tokens.text.secondary,
          border: `1px solid ${tokens.border.subtle}`,
          '&:hover': {
            backgroundColor: alpha(tokens.accent.primary, 0.08),
            color: tokens.text.primary,
          },
        };

        return {
          minHeight: 44,
          borderRadius: `${tokens.radius.pill}px`,
          px: 2,
          boxShadow: 'none',
          fontWeight: 700,
          ...(tone === 'primary' ? primaryStyles : tone === 'secondary' ? secondaryStyles : ghostStyles),
          '&.Mui-disabled': {
            opacity: 0.55,
            color: tokens.text.muted,
            background: alpha(tokens.text.muted, 0.12),
            borderColor: alpha(tokens.text.muted, 0.14),
          },
        };
      },
      sx,
    )}
  >
    {children}
  </Button>
);

interface UiIconButtonProps extends IconButtonProps {
  tone?: UiIconTone;
}

export const UiIconButton = ({ tone = 'neutral', sx, children, ...props }: UiIconButtonProps) => (
  <IconButton
    {...props}
    sx={mergeSx(
      (theme) => {
        const tokens = resolveTokens(theme);
        const toneStyles = {
          primary: {
            background: `linear-gradient(135deg, ${tokens.accent.primary}, ${tokens.accent.primaryHover})`,
            color: tokens.text.inverse,
            border: 'none',
            '&:hover': {
              background: `linear-gradient(135deg, ${tokens.accent.primaryHover}, ${tokens.accent.primaryActive})`,
            },
          },
          neutral: {
            backgroundColor: tokens.surface.secondary,
            color: tokens.text.secondary,
            border: `1px solid ${tokens.border.subtle}`,
            '&:hover': {
              backgroundColor: tokens.surface.tertiary,
              color: tokens.text.primary,
            },
          },
          ghost: {
            backgroundColor: 'transparent',
            color: tokens.text.secondary,
            border: '1px solid transparent',
            '&:hover': {
              backgroundColor: alpha(tokens.accent.primary, 0.08),
              color: tokens.text.primary,
            },
          },
        } as const;

        return {
          width: 44,
          height: 44,
          borderRadius: `${tokens.radius.pill}px`,
          transition: theme.transitions.create(['background-color', 'transform', 'color', 'border-color']),
          ...toneStyles[tone],
          '&:active': {
            transform: 'translateY(1px)',
          },
          '&.Mui-disabled': {
            opacity: 0.5,
            color: tokens.text.muted,
            backgroundColor: alpha(tokens.text.muted, 0.1),
            borderColor: alpha(tokens.text.muted, 0.12),
          },
        };
      },
      sx,
    )}
  >
    {children}
  </IconButton>
);

export const UiPromptField = ({ sx, InputProps, ...props }: TextFieldProps) => (
  <TextField
    {...props}
    InputProps={{
      ...InputProps,
    }}
    sx={mergeSx(
      (theme) => {
        const tokens = resolveTokens(theme);

        return {
          '& .MuiOutlinedInput-root': {
            borderRadius: `${tokens.radius.md}px`,
            backgroundColor: alpha(tokens.surface.secondary, theme.palette.mode === 'light' ? 0.76 : 0.92),
            color: tokens.text.primary,
            alignItems: 'flex-end',
            transition: theme.transitions.create(['border-color', 'box-shadow', 'background-color']),
            '& fieldset': {
              borderColor: tokens.border.subtle,
            },
            '&:hover fieldset': {
              borderColor: tokens.border.strong,
            },
            '&.Mui-focused': {
              backgroundColor: tokens.surface.primary,
              boxShadow: `0 0 0 4px ${alpha(tokens.accent.primary, 0.14)}`,
            },
            '&.Mui-focused fieldset': {
              borderColor: tokens.accent.primary,
            },
          },
          '& .MuiInputBase-input::placeholder': {
            color: tokens.text.muted,
            opacity: 1,
          },
        };
      },
      sx,
    )}
  />
);

interface UiChatBubbleProps extends PaperProps {
  isCurrentUser: boolean;
  children: ReactNode;
}

export const UiChatBubble = ({ isCurrentUser, sx, children, ...props }: UiChatBubbleProps) => (
  <Paper
    elevation={0}
    {...props}
    sx={mergeSx(
      (theme) => {
        const tokens = resolveTokens(theme);

        return {
          background: tokens.surface.primary,
          color: tokens.text.primary,
          border: `1px solid ${tokens.border.subtle}`,
          borderRadius: isCurrentUser
            ? `${tokens.radius.lg}px ${tokens.radius.lg}px 8px ${tokens.radius.lg}px`
            : `${tokens.radius.lg}px ${tokens.radius.lg}px ${tokens.radius.lg}px 8px`,
          boxShadow: 'none',
          backdropFilter: 'blur(18px)',
        };
      },
      sx,
    )}
  >
    {children}
  </Paper>
);

interface UiParticipantAvatarProps extends AvatarProps {
  isCurrentUser: boolean;
  label?: string;
}

export const UiParticipantAvatar = ({ isCurrentUser, label, sx, children, ...props }: UiParticipantAvatarProps) => (
  <Avatar
    {...props}
    sx={mergeSx(
      (theme) => {
        const tokens = resolveTokens(theme);

        return {
          width: 36,
          height: 36,
          fontSize: '0.85rem',
          fontWeight: 700,
          color: isCurrentUser ? tokens.text.inverse : tokens.text.primary,
          background: isCurrentUser
            ? `linear-gradient(145deg, ${tokens.accent.primary}, ${tokens.accent.primaryHover})`
            : alpha(tokens.surface.tertiary, 0.95),
          border: `1px solid ${isCurrentUser ? alpha(tokens.text.inverse, 0.18) : tokens.border.subtle}`,
          boxShadow: tokens.shadow.soft,
        };
      },
      sx,
    )}
  >
    {children ?? label ?? (isCurrentUser ? <PersonRounded fontSize="small" /> : <SmartToyOutlined fontSize="small" />)}
  </Avatar>
);

interface UiLoadingDotsProps extends BoxProps {
  isCurrentUser?: boolean;
}

export const UiLoadingDots = ({ isCurrentUser = false, sx, ...props }: UiLoadingDotsProps) => (
  <Box
    {...props}
    sx={mergeSx(
      {
        display: 'flex',
        alignItems: 'center',
        gap: 0.75,
      },
      sx,
    )}
  >
    {[0, 1, 2].map((index) => (
      <Box
        key={index}
        sx={(theme) => {
          const tokens = resolveTokens(theme);

          return {
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: isCurrentUser ? alpha(tokens.text.inverse, 0.92) : tokens.text.secondary,
            animation: 'uiDotPulse 1.25s infinite ease-in-out',
            animationDelay: `${index * 0.14}s`,
            '@keyframes uiDotPulse': {
              '0%, 70%, 100%': { transform: 'translateY(0)', opacity: 0.45 },
              '35%': { transform: 'translateY(-5px)', opacity: 1 },
            },
          };
        }}
      />
    ))}
  </Box>
);

interface UiMessageSkeletonProps {
  align?: 'left' | 'right';
}

export const UiMessageSkeleton = ({ align = 'left' }: UiMessageSkeletonProps) => {
  const isCurrentUser = align === 'right';

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isCurrentUser ? 'flex-end' : 'flex-start',
        alignItems: 'flex-start',
        gap: 1.25,
      }}
    >
      {!isCurrentUser && <UiParticipantAvatar isCurrentUser={false} />}
      <Box sx={{ width: { xs: '78%', sm: '60%' } }}>
        <UiChatBubble
          isCurrentUser={isCurrentUser}
          sx={{
            p: 2,
            opacity: 0.88,
          }}
        >
          <Skeleton variant="text" width="68%" height={18} />
          <Skeleton variant="text" width="100%" height={18} />
          <Skeleton variant="text" width="82%" height={18} />
        </UiChatBubble>
      </Box>
      {isCurrentUser && <UiParticipantAvatar isCurrentUser />}
    </Box>
  );
};

interface UiEmptyStateProps extends BoxProps {
  title: string;
  description?: string;
  icon?: ReactNode;
}

export const UiEmptyState = ({ title, description, icon, sx, ...props }: UiEmptyStateProps) => (
  <Box
    {...props}
    sx={mergeSx(
      (theme) => {
        const tokens = resolveTokens(theme);

        return {
          minHeight: 240,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: 1.25,
          borderRadius: `${tokens.radius.lg}px`,
          border: `1px dashed ${tokens.border.strong}`,
          background: `linear-gradient(180deg, ${alpha(tokens.surface.secondary, 0.82)}, transparent)`,
          px: 3,
        };
      },
      sx,
    )}
  >
    {icon && <Box sx={{ color: 'text.secondary' }}>{icon}</Box>}
    <Typography variant="h6">{title}</Typography>
    {description && (
      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 420 }}>
        {description}
      </Typography>
    )}
  </Box>
);