import type { SxProps, Theme } from '@mui/material';

/**
 * Reusable navigation item styles for consistent UI across the navigation drawer
 * Use these styles for any navigation-like list items (navigation items, settings items, session items)
 */

/**
 * Common styles for list item buttons in navigation drawer
 * Provides consistent selected state and hover effects
 */
export const getNavigationItemStyles = (): SxProps<Theme> => ({
  borderRadius: '16px',
  border: '1px solid transparent',
  px: 1.25,
  py: 0.5,
  transition: (theme) => theme.transitions.create(['background-color', 'border-color', 'color', 'transform']),
  '&:hover': {
    backgroundColor: 'color-mix(in srgb, var(--accent-primary) 8%, transparent)',
    borderColor: 'var(--border-subtle)',
  },
  '&.Mui-selected': {
    backgroundColor: 'color-mix(in srgb, var(--accent-primary) 14%, transparent)',
    borderColor: 'color-mix(in srgb, var(--accent-primary) 36%, transparent)',
    color: 'text.primary',
  },
  '&.Mui-selected:hover': {
    backgroundColor: 'color-mix(in srgb, var(--accent-primary) 18%, transparent)',
  },
});

/**
 * Styles for navigation items with icons (Home, Settings, etc.)
 * Includes border radius for visual distinction
 */
export const getNavigationItemWithIconStyles = (): SxProps<Theme> => ({
  mx: 1,
  ...getNavigationItemStyles(),
});

/**
 * Styles for settings items list
 * Similar to navigation items but without horizontal margin
 */
export const getSettingsItemStyles = (): SxProps<Theme> => ({
  mb: 0.5,
  ...getNavigationItemStyles(),
});

