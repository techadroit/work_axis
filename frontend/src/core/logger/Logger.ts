import * as Sentry from '@sentry/react';
import type { LoggerConfig } from './config';
import { defaultLoggerConfig } from './config';

/**
 * Log Level Enum
 */
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  FATAL = 'fatal',
}

/**
 * Logger Wrapper Class
 * Provides a centralized logging interface with Sentry integration
 */
export class Logger {
  private static instance: Logger | null = null;
  private isInitialized = false;
  private config: LoggerConfig;

  private constructor(config?: LoggerConfig) {
    this.config = { ...defaultLoggerConfig, ...config };
  }

  /**
   * Get Logger singleton instance
   */
  public static getInstance(config?: LoggerConfig): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger(config);
    }
    return Logger.instance;
  }

  /**
   * Initialize Sentry
   */
  public init(config?: LoggerConfig): void {
    if (this.isInitialized) {
      console.warn('[Logger] Already initialized');
      return;
    }

    if (config) {
      this.config = { ...this.config, ...config };
    }

    if (!this.config.enabled) {
      console.info('[Logger] Sentry logging is disabled');
      return;
    }

    if (!this.config.dsn) {
      console.warn('[Logger] Sentry DSN not configured. Logging to console only.');
      return;
    }

    try {
      Sentry.init({
        dsn: this.config.dsn,
        environment: this.config.environment,
        release: this.config.release,
        tracesSampleRate: this.config.tracesSampleRate,
        integrations: [
          Sentry.browserTracingIntegration(),
          Sentry.replayIntegration(),
        ],
      });

      this.isInitialized = true;
      console.info('[Logger] Sentry initialized successfully');
    } catch (error) {
      console.error('[Logger] Failed to initialize Sentry:', error);
    }
  }

  /**
   * Log debug message
   */
  public debug(message: string, context?: Record<string, any>): void {
    console.debug(`[DEBUG] ${message}`, context);

    if (this.isInitialized) {
      Sentry.captureMessage(message, {
        level: 'debug',
        contexts: context ? { extra: context } : undefined,
      });
    }
  }

  /**
   * Log info message
   */
  public info(message: string, context?: Record<string, any>): void {
    console.info(`[INFO] ${message}`, context);

    if (this.isInitialized) {
      Sentry.captureMessage(message, {
        level: 'info',
        contexts: context ? { extra: context } : undefined,
      });
    }
  }

  /**
   * Log warning message
   */
  public warn(message: string, context?: Record<string, any>): void {
    console.warn(`[WARN] ${message}`, context);

    if (this.isInitialized) {
      Sentry.captureMessage(message, {
        level: 'warning',
        contexts: context ? { extra: context } : undefined,
      });
    }
  }

  /**
   * Log error message
   */
  public error(message: string, error?: Error | unknown, context?: Record<string, any>): void {
    console.error(`[ERROR] ${message}`, error, context);

    if (this.isInitialized) {
      if (error instanceof Error) {
        Sentry.captureException(error, {
          contexts: context ? { extra: context } : undefined,
          tags: { message },
        });
      } else {
        Sentry.captureMessage(message, {
          level: 'error',
          contexts: context ? { extra: context } : undefined,
        });
      }
    }
  }

  /**
   * Log fatal error message
   */
  public fatal(message: string, error?: Error | unknown, context?: Record<string, any>): void {
    console.error(`[FATAL] ${message}`, error, context);

    if (this.isInitialized) {
      if (error instanceof Error) {
        Sentry.captureException(error, {
          level: 'fatal',
          contexts: context ? { extra: context } : undefined,
          tags: { message },
        });
      } else {
        Sentry.captureMessage(message, {
          level: 'fatal',
          contexts: context ? { extra: context } : undefined,
        });
      }
    }
  }

  /**
   * Set user context for logging
   */
  public setUser(userId: string, userData?: Record<string, any>): void {
    if (this.isInitialized) {
      Sentry.setUser({
        id: userId,
        ...userData,
      });
    }
  }

  /**
   * Clear user context
   */
  public clearUser(): void {
    if (this.isInitialized) {
      Sentry.setUser(null);
    }
  }

  /**
   * Add breadcrumb for debugging
   */
  public addBreadcrumb(message: string, data?: Record<string, any>, level?: LogLevel): void {
    if (this.isInitialized) {
      Sentry.addBreadcrumb({
        message,
        data,
        level: level || LogLevel.INFO,
        timestamp: Date.now(),
      });
    }
  }

  /**
   * Set custom context
   */
  public setContext(key: string, context: Record<string, any>): void {
    if (this.isInitialized) {
      Sentry.setContext(key, context);
    }
  }

  /**
   * Capture exception manually
   */
  public captureException(error: Error, context?: Record<string, any>): void {
    console.error('[EXCEPTION]', error, context);

    if (this.isInitialized) {
      Sentry.captureException(error, {
        contexts: context ? { extra: context } : undefined,
      });
    }
  }

  /**
   * Check if logger is initialized
   */
  public isReady(): boolean {
    return this.isInitialized;
  }
}

// Export singleton instance
export const logger = Logger.getInstance();

