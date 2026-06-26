import { configureStore } from '@reduxjs/toolkit';
import { createContext } from 'react';
import { createDispatchHook, createSelectorHook, type ReactReduxContextValue } from 'react-redux';
import chatReducer from './chatSlice';
import fileUploadReducer from './fileUploadSlice';

/**
 * Chat Store - Separate store for chat functionality
 */
export const chatStore = configureStore({
  reducer: {
    chat: chatReducer,
    fileUpload: fileUploadReducer,
  },
});

// Types
export type ChatStoreState = ReturnType<typeof chatStore.getState>;
export type ChatStoreDispatch = typeof chatStore.dispatch;

// Create a custom context for this store
export const ChatStoreContext = createContext<ReactReduxContextValue<ChatStoreState, any> | null>(null);

// Create hooks that use the custom ChatStoreContext with proper typing
export const useChatDispatch = createDispatchHook(ChatStoreContext) as () => ChatStoreDispatch;
export const useChatSelector = createSelectorHook(ChatStoreContext) as <TSelected>(
  selector: (state: ChatStoreState) => TSelected,
  equalityFn?: (left: TSelected, right: TSelected) => boolean
) => TSelected;

