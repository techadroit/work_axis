import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { ModelProvider, SavedProviderConfig } from '../types';
import { ModelProviderApi } from '../../../data/api/ModelProviderApi';
import { logger } from '../../../core/logger';

interface ModelProviderState {
  providers: ModelProvider[];
  savedProviders: SavedProviderConfig[];
  loading: boolean;
  loadingSavedProviders: boolean;
  error: string | null;
}

const initialState: ModelProviderState = {
  providers: [],
  savedProviders: [],
  loading: false,
  loadingSavedProviders: false,
  error: null,
};

/**
 * Load all available model providers
 */
export const loadModelProviders = createAsyncThunk(
  'modelProvider/loadModelProviders',
  async (_, { rejectWithValue }) => {
    try {
      logger.info('Loading model providers');
      const providers = await ModelProviderApi.getAllModelProviders();
      logger.info('Model providers loaded successfully', { count: providers.length });
      return providers;
    } catch (error) {
      logger.error('Failed to load model providers', error);
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load model providers');
    }
  }
);

/**
 * Load saved provider configurations
 */
export const loadSavedProviders = createAsyncThunk(
  'modelProvider/loadSavedProviders',
  async (_, { rejectWithValue }) => {
    try {
      logger.info('Loading saved provider configurations');
      const savedProviders = await ModelProviderApi.getSavedProviders();
      logger.info('Saved provider configurations loaded successfully', { count: savedProviders.length });
      return savedProviders;
    } catch (error) {
      logger.error('Failed to load saved provider configurations', error);
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load saved providers');
    }
  }
);

const modelProviderSlice = createSlice({
  name: 'modelProvider',
  initialState,
  reducers: {
    clearProviders: (state) => {
      state.providers = [];
      logger.info('Model providers cleared');
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadModelProviders.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loadModelProviders.fulfilled, (state, action) => {
        state.loading = false;
        state.providers = action.payload;
      })
      .addCase(loadModelProviders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        logger.error('Failed to load model providers', { error: action.payload });
      })
      .addCase(loadSavedProviders.pending, (state) => {
        state.loadingSavedProviders = true;
        state.error = null;
      })
      .addCase(loadSavedProviders.fulfilled, (state, action) => {
        state.loadingSavedProviders = false;
        state.savedProviders = action.payload;
      })
      .addCase(loadSavedProviders.rejected, (state, action) => {
        state.loadingSavedProviders = false;
        state.error = action.payload as string;
        logger.error('Failed to load saved providers', { error: action.payload });
      });
  },
});

export const { clearProviders } = modelProviderSlice.actions;
export default modelProviderSlice.reducer;

