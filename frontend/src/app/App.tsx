import { useEffect, useMemo } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AppRouter from './AppRouter';
import './App.css';
import { logger } from '../core/logger';
import { createAppTheme } from '../design_system/theme';

function App() {
  const prefersDarkMode = false//useMediaQuery('(prefers-color-scheme: dark)', { noSsr: true });
  const theme = useMemo(
    () => createAppTheme(prefersDarkMode ? 'dark' : 'light'),
    [prefersDarkMode],
  );

  useEffect(() => {
    // Initialize logger on app startup
    logger.init();
    logger.info('Application started');
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppRouter />
    </ThemeProvider>
  );
}

export default App;
