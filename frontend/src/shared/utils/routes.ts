/**
 * Navigation Routes Constants
 *
 * Centralized definition of all application routes.
 * Use these constants throughout the application for consistent navigation.
 */

/**
 * Main navigation routes
 */
export const ROUTES = {
  /** Home page route */
  HOME: '/',

  /** Chat routes */
  CHAT: '/chat',
  /** Chat with specific session ID - use with template: `${ROUTES.CHAT}/${sessionId}` */
  CHAT_SESSION: '/chat/:sessionId',

  /** Settings routes */
  SETTINGS: '/settings',
  SETTINGS_GENERAL: '/settings/general',
  SETTINGS_MODELS: '/settings/models',
} as const;

/**
 * Helper function to generate chat session route with ID
 * @param sessionId - The chat session ID
 * @returns The complete route path
 */
export const getChatSessionRoute = (sessionId: string): string => {
  return `${ROUTES.CHAT}/${sessionId}`;
};

/**
 * Type for route values
 */
export type RouteValue = typeof ROUTES[keyof typeof ROUTES];

