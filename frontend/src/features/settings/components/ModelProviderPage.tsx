import { Provider } from 'react-redux';
import { Box } from '@mui/material';
import { ModelProviderScreen, settingsStore, SettingsStoreContext } from '../index';

/**
 * Example: ModelProviderPage - Full page with Redux provider
 * Use this as a reference for integrating the ModelProviderScreen into your app
 */
export const ModelProviderPage = () => {
  return (
    <Provider store={settingsStore} context={SettingsStoreContext}>
      <Box
        sx={{
          width: '100%',
          height: '100%',
          overflow: 'hidden',
        }}
      >
        <ModelProviderScreen />
      </Box>
    </Provider>
  );
};

