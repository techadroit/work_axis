import {createSlice, type PayloadAction} from '@reduxjs/toolkit';
import {loadUser} from '../hooks/useLoadUser';
import { logger } from '../../core/logger';

interface UserState {
  userId: string | null;
  loading: boolean;
  error: string | null;
}

const initialState: UserState = {
  userId: null,
  loading: false,
  error: null,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUserId: (state, action: PayloadAction<string>) => {
      state.userId = action.payload;
      logger.info('User ID set', { userId: action.payload });
    },
    clearUser: (state) => {
      state.userId = null;
      logger.info('User cleared');
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadUser.pending, (state) => {
        logger.addBreadcrumb('loadUser.pending', { loading: true });
        state.loading = true;
        state.error = null;
      })
      .addCase(loadUser.fulfilled, (state, action: PayloadAction<string>) => {
        logger.addBreadcrumb('loadUser.fulfilled', { userId: action.payload });
        state.loading = false;
        state.userId = action.payload;
        state.error = null;

        // Set user context in logger for better error tracking
        logger.setUser(action.payload);
      })
      .addCase(loadUser.rejected, (state, action) => {
        logger.error('loadUser.rejected', undefined, { error: action.payload });
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setUserId, clearUser } = userSlice.actions;
export default userSlice.reducer;

