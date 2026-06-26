/**
 * Logger Configuration
 * Configure Sentry DSN and other logging settings here
 */

export interface LoggerConfig {
  dsn?: string;
  environment?: string;
  release?: string;
  tracesSampleRate?: number;
  enabled?: boolean;
}

export const defaultLoggerConfig: LoggerConfig = {
  dsn: import.meta.env.VITE_SENTRY_DSN || '',
  environment: import.meta.env.MODE || 'development',
  release: import.meta.env.VITE_APP_VERSION || '0.0.0',
  tracesSampleRate: 1.0,
  enabled: import.meta.env.PROD || false, // Only enable in production by default
};

