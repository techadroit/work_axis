import {
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import type { ReactNode } from 'react';
import { getNavigationItemWithIconStyles } from '../../../design_system/styles/navigation_styles/navigationStyles.ts';

interface NavigationItemProps {
  text: string;
  icon: ReactNode;
  isSelected: boolean;
  onClick: () => void;
}

/**
 * NavigationItem Component
 * Reusable navigation item with consistent styling and hover effects
 */
export const NavigationItem = ({ text, icon, isSelected, onClick }: NavigationItemProps) => {
  return (
    <ListItem disablePadding sx={{ mb: 0.5 }}>
      <ListItemButton
        onClick={onClick}
        selected={isSelected}
        sx={getNavigationItemWithIconStyles()}
      >
        <ListItemIcon
          sx={{
            minWidth: 40,
            color: isSelected ? 'primary.main' : 'text.secondary',
          }}
        >
          {icon}
        </ListItemIcon>
        <ListItemText
          primary={text}
          slotProps={{
            primary: {
              sx: {
                fontWeight: isSelected ? 700 : 600,
              },
            },
          }}
        />
      </ListItemButton>
    </ListItem>
  );
};

