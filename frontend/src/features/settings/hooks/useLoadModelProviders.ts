import { useEffect } from 'react';
import { useSettingsDispatch, useSettingsSelector } from '../stores/settingsStore';
import { loadModelProviders } from '../stores/modelProviderSlice';

/**
 * Hook to load model providers
 */
export const useLoadModelProviders = () => {
  const dispatch = useSettingsDispatch();
  const { providers, loading, error } = useSettingsSelector((state) => state.modelProvider);

  useEffect(() => {
    // Only load if we haven't loaded providers yet and we're not currently loading
    if (providers.length === 0 && !loading && !error) {
      dispatch(loadModelProviders());
    }
  }, [dispatch, providers.length, loading, error]);

  return { providers, loading, error };
};

