import { configureStore } from '@reduxjs/toolkit';
import { createContext } from 'react';
import { createDispatchHook, createSelectorHook, type ReactReduxContextValue } from 'react-redux';
import modelProviderReducer from './modelProviderSlice';

/**
 * Settings Store - Separate store for settings functionality
 */
export const settingsStore = configureStore({
  reducer: {
    modelProvider: modelProviderReducer,
  },
});

// Types
export type SettingsStoreState = ReturnType<typeof settingsStore.getState>;
export type SettingsStoreDispatch = typeof settingsStore.dispatch;

// Create a custom context for this store
export const SettingsStoreContext = createContext<ReactReduxContextValue<SettingsStoreState, any> | null>(null);

// Create hooks that use the custom SettingsStoreContext with proper typing
export const useSettingsDispatch = createDispatchHook(SettingsStoreContext) as () => SettingsStoreDispatch;
export const useSettingsSelector = createSelectorHook(SettingsStoreContext) as <TSelected>(
  selector: (state: SettingsStoreState) => TSelected,
  equalityFn?: (left: TSelected, right: TSelected) => boolean
) => TSelected;

