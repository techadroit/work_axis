import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';
import { createContext } from 'react';
import { createDispatchHook, createSelectorHook, type ReactReduxContextValue } from 'react-redux';

export const userStore = configureStore({
  reducer: {
    user: userReducer,
  },
});

// Create a separate context for userStore to avoid nested Provider conflicts
export const UserStoreContext = createContext<ReactReduxContextValue<UserStoreState, any> | null>(null);

export type UserStoreState = ReturnType<typeof userStore.getState>;
export type UserDispatch = typeof userStore.dispatch;

// Create hooks that use the custom UserStoreContext with proper typing
export const useUserDispatch = createDispatchHook(UserStoreContext) as () => UserDispatch;
export const useUserSelector = createSelectorHook(UserStoreContext) as <TSelected>(
  selector: (state: UserStoreState) => TSelected,
  equalityFn?: (left: TSelected, right: TSelected) => boolean
) => TSelected;

