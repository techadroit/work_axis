import { List, ListItem, ListItemButton, ListItemIcon, ListItemText, Box } from '@mui/material';
import { Settings as SettingsIcon, SmartToy as SmartToyIcon, Mail as MailIcon } from '@mui/icons-material';
import { getSettingsItemStyles } from '../../../design_system/styles/navigation_styles/navigationStyles.ts';
import { ROUTES } from '../../../shared/utils';
import { UiSectionTitle } from '../../../shared/components/ui';

interface SettingsItem {
  text: string;
  icon: React.ReactNode;
  path: string;
}

interface SettingsItemListProps {
  onSelectItem: (path: string) => void;
  selectedPath?: string;
}

const settingsItems: SettingsItem[] = [
  { text: 'General', icon: <SettingsIcon />, path: ROUTES.SETTINGS_GENERAL },
  { text: 'Model Provider', icon: <SmartToyIcon />, path: ROUTES.SETTINGS_MODELS },
  { text: 'Email Integrations', icon: <MailIcon />, path: ROUTES.SETTINGS_EMAIL_INTEGRATIONS },
];

/**
 * SettingsItemList Component
 * Displays a list of settings options in the navigation drawer
 */
export const SettingsItemList = ({ onSelectItem, selectedPath }: SettingsItemListProps) => {
  return (
    <Box sx={{ px: 2, py: 1 }}>
      <UiSectionTitle eyebrow="Navigation" sx={{ mb: 1.5 }}>
        Settings
      </UiSectionTitle>
      <List disablePadding>
        {settingsItems.map((item) => {
          const isSelected = selectedPath === item.path;
          return (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                onClick={() => onSelectItem(item.path)}
                selected={isSelected}
                sx={getSettingsItemStyles()}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isSelected ? 'primary.main' : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
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
        })}
      </List>
    </Box>
  );
};

