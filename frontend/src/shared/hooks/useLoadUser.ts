import { createAsyncThunk } from '@reduxjs/toolkit';
import { UserService } from '../../data/services/UserService';
import { logger } from '../../core/logger';

/**
 * Async thunk to load user
 * Delegates business logic to UserService
 */
export const loadUser = createAsyncThunk(
  'user/loadUser',
  async (_, { rejectWithValue }) => {
    try {
      const userService = new UserService();
      const userId = await userService.loadOrCreateUser();
      return userId;
    } catch (error) {
      logger.error('Failed to load user', error);
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load user');
    }
  }
);
