import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { EmailAccount } from '../types';
import { EmailIntegrationApi } from '../../../data/api/EmailIntegrationApi';
import { logger } from '../../../core/logger';

interface EmailIntegrationState {
  accounts: EmailAccount[];
  loading: boolean;
  // Tracks whether at least one fetch has completed. The load-on-mount hook
  // must guard on this rather than accounts.length === 0: an empty accounts
  // list is a normal steady state (user has no accounts yet), and using
  // length as the guard causes an infinite refetch loop for such users.
  loaded: boolean;
  error: string | null;
}

const initialState: EmailIntegrationState = {
  accounts: [],
  loading: false,
  loaded: false,
  error: null,
};

/**
 * Load connected email accounts for a user
 */
export const loadEmailAccounts = createAsyncThunk(
  'emailIntegration/loadEmailAccounts',
  async (userId: string, { rejectWithValue }) => {
    try {
      logger.info('Loading email accounts', { userId });
      const accounts = await EmailIntegrationApi.getAccounts(userId);
      logger.info('Email accounts loaded successfully', { count: accounts.length });
      return accounts;
    } catch (error) {
      logger.error('Failed to load email accounts', error);
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load email accounts');
    }
  }
);

const emailIntegrationSlice = createSlice({
  name: 'emailIntegration',
  initialState,
  reducers: {
    clearEmailAccounts: (state) => {
      state.accounts = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadEmailAccounts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loadEmailAccounts.fulfilled, (state, action) => {
        state.loading = false;
        state.loaded = true;
        state.accounts = action.payload;
      })
      .addCase(loadEmailAccounts.rejected, (state, action) => {
        state.loading = false;
        state.loaded = true;
        state.error = action.payload as string;
        logger.error('Failed to load email accounts', { error: action.payload });
      });
  },
});

export const { clearEmailAccounts } = emailIntegrationSlice.actions;
export default emailIntegrationSlice.reducer;
