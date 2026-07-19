import { Provider } from 'react-redux';
import { Box } from '@mui/material';
import { EmailIntegrationScreen, settingsStore, SettingsStoreContext } from '../index';

export const EmailIntegrationPage = () => {
  return (
    <Provider store={settingsStore} context={SettingsStoreContext}>
      <Box
        sx={{
          width: '100%',
          height: '100%',
          overflow: 'hidden',
        }}
      >
        <EmailIntegrationScreen />
      </Box>
    </Provider>
  );
};
