import { useState, useEffect } from 'react';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';

/**
 * Custom hook to manage drawer state
 * - Open by default on large screens
 * - Collapsed by default on small and medium screens
 */
export const useDrawer = () => {
  const theme = useTheme();
  const isLargeScreen = useMediaQuery(theme.breakpoints.up('lg'));

  const [isOpen, setIsOpen] = useState(isLargeScreen);

  // Update drawer state when screen size changes
  useEffect(() => {
    setIsOpen(isLargeScreen);
  }, [isLargeScreen]);

  const toggleDrawer = () => {
    setIsOpen(!isOpen);
  };

  const openDrawer = () => {
    setIsOpen(true);
  };

  const closeDrawer = () => {
    setIsOpen(false);
  };

  return {
    isOpen,
    isLargeScreen,
    toggleDrawer,
    openDrawer,
    closeDrawer,
  };
};

