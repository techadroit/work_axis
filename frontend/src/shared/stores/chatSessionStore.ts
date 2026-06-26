import { configureStore } from '@reduxjs/toolkit';
import { createContext } from 'react';
import { createDispatchHook, createSelectorHook, type ReactReduxContextValue } from 'react-redux';
import chatSessionReducer from './chatSessionSlice';

export const chatSessionStore = configureStore({
  reducer: {
    chatSession: chatSessionReducer,
  },
});

// Create a separate context for chatSessionStore to avoid nested Provider conflicts
export const ChatSessionStoreContext = createContext<ReactReduxContextValue<ChatSessionStoreState, any> | null>(null);

export type ChatSessionStoreState = ReturnType<typeof chatSessionStore.getState>;
export type ChatSessionDispatch = typeof chatSessionStore.dispatch;

// Create hooks that use the custom ChatSessionStoreContext with proper typing
export const useChatSessionDispatch = createDispatchHook(ChatSessionStoreContext) as () => ChatSessionDispatch;
export const useChatSessionSelector = createSelectorHook(ChatSessionStoreContext) as <TSelected>(
  selector: (state: ChatSessionStoreState) => TSelected,
  equalityFn?: (left: TSelected, right: TSelected) => boolean
) => TSelected;

