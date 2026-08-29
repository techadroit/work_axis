import { useEffect } from 'react';
import { useSettingsDispatch, useSettingsSelector } from '../stores/settingsStore';
import { loadEmailAccounts } from '../stores/emailIntegrationSlice';

/**
 * Hook to load connected email accounts for a user
 */
export const useLoadEmailAccounts = (userId: string | null) => {
  const dispatch = useSettingsDispatch();
  const { accounts, loading, loaded, error } = useSettingsSelector((state) => state.emailIntegration);

  useEffect(() => {
    // Guard on `loaded`, NOT accounts.length: an empty list is a valid
    // steady state (no accounts connected yet) and guarding on length
    // causes an infinite refetch loop for zero-account users.
    if (userId && !loaded && !loading) {
      dispatch(loadEmailAccounts(userId));
    }
  }, [dispatch, userId, loaded, loading]);

  return { accounts, loading, error };
};
