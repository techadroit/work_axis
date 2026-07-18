import { logger } from '../../core/logger';

/**
 * WebSocket connection states
 */
export enum ConnectionState {
  DISCONNECTED = 'DISCONNECTED',
  CONNECTING = 'CONNECTING',
  CONNECTED = 'CONNECTED',
  RECONNECTING = 'RECONNECTING',
  FAILED = 'FAILED',
}

/**
 * MessageService - Handles WebSocket connections for real-time messaging
 */
export class MessageService {
  private ws: WebSocket | null = null;
  private userId: string | null = null;
  private baseURL: string;
  private retryCount: number = 0;
  private maxRetries: number = 5;
  private retryTimeoutId: ReturnType<typeof setTimeout> | null = null;
  private connectionState: ConnectionState = ConnectionState.DISCONNECTED;
  private messageHandlers: Set<(message: any) => void> = new Set();
  private stateChangeHandlers: Set<(state: ConnectionState) => void> = new Set();

  constructor(baseURL: string = 'ws://127.0.0.1:8001/ws') {
    this.baseURL = baseURL;
  }

  /**
   * Get current connection state
   */
  getConnectionState(): ConnectionState {
    return this.connectionState;
  }

  /**
   * Set connection state and notify handlers
   */
  private setConnectionState(state: ConnectionState): void {
    this.connectionState = state;
    logger.info('WebSocket connection state changed', { state });
    this.stateChangeHandlers.forEach(handler => handler(state));
  }

  /**
   * Connect to WebSocket with user ID
   */
  connect(userId: string): void {
    if (!userId) {
      logger.error('Cannot connect to WebSocket: userId is required');
      return;
    }

    this.userId = userId;

    // If already connected or connecting, don't create a new connection
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      logger.info('WebSocket already connected or connecting');
      return;
    }

    this.createConnection();
  }

  /**
   * Create WebSocket connection
   */
  private createConnection(): void {
    if (!this.userId) {
      logger.error('Cannot create connection: userId is not set');
      return;
    }

    try {
      const wsUrl = `${this.baseURL}/${this.userId}`;
      logger.info('Connecting to WebSocket', { url: wsUrl, retryCount: this.retryCount });

      this.setConnectionState(
        this.retryCount > 0 ? ConnectionState.RECONNECTING : ConnectionState.CONNECTING
      );

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
    } catch (error) {
      logger.error('Failed to create WebSocket connection', error);
      this.handleConnectionFailure();
    }
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen(): void {
    logger.info('WebSocket connected successfully');
    this.retryCount = 0; // Reset retry count on successful connection
    this.setConnectionState(ConnectionState.CONNECTED);

    // Clear any pending retry timeout
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId);
      this.retryTimeoutId = null;
    }
  }

  /**
   * Handle WebSocket message event
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message = JSON.parse(event.data);
      logger.info('WebSocket message received', { message });

      // Notify all message handlers
      this.messageHandlers.forEach(handler => handler(message));
    } catch (error) {
      logger.error('Failed to parse WebSocket message', error, { data: event.data });
    }
  }

  /**
   * Handle WebSocket error event
   */
  private handleError(event: Event): void {
    logger.error('WebSocket error occurred', undefined, { event });
  }

  /**
   * Handle WebSocket close event
   */
  private handleClose(event: CloseEvent): void {
    logger.info('WebSocket connection closed', {
      code: event.code,
      reason: event.reason,
      wasClean: event.wasClean
    });

    // If connection was closed intentionally (by calling disconnect), don't retry
    if (this.connectionState === ConnectionState.DISCONNECTED) {
      return;
    }

    this.handleConnectionFailure();
  }

  /**
   * Handle connection failure and retry logic
   */
  private handleConnectionFailure(): void {
    if (this.retryCount >= this.maxRetries) {
      logger.error('WebSocket connection failed: max retries reached', undefined, {
        retryCount: this.retryCount,
        maxRetries: this.maxRetries
      });
      this.setConnectionState(ConnectionState.FAILED);
      return;
    }

    // Calculate retry delay: 3 seconds * retry attempt (1, 2, 3, 4, 5)
    const retryDelay = 3000 * (this.retryCount + 1);
    this.retryCount++;

    logger.info('Scheduling WebSocket reconnection', {
      retryCount: this.retryCount,
      retryDelay,
      maxRetries: this.maxRetries
    });

    this.setConnectionState(ConnectionState.RECONNECTING);

    // Schedule retry
    this.retryTimeoutId = setTimeout(() => {
      this.createConnection();
    }, retryDelay);
  }

  /**
   * Send message through WebSocket
   */
  sendMessage(message: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      logger.error('Cannot send message: WebSocket is not connected');
      throw new Error('WebSocket is not connected');
    }

    try {
      const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
      this.ws.send(messageStr);
      logger.info('Message sent via WebSocket', { message });
    } catch (error) {
      logger.error('Failed to send WebSocket message', error);
      throw error;
    }
  }

  /**
   * Register a message handler
   */
  onMessage(handler: (message: any) => void): () => void {
    this.messageHandlers.add(handler);

    // Return unsubscribe function
    return () => {
      this.messageHandlers.delete(handler);
    };
  }

  /**
   * Register a connection state change handler
   */
  onStateChange(handler: (state: ConnectionState) => void): () => void {
    this.stateChangeHandlers.add(handler);

    // Return unsubscribe function
    return () => {
      this.stateChangeHandlers.delete(handler);
    };
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect(): void {
    logger.info('Disconnecting WebSocket');

    // Clear any pending retry timeout
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId);
      this.retryTimeoutId = null;
    }

    // Set state to disconnected before closing
    this.setConnectionState(ConnectionState.DISCONNECTED);

    // Close WebSocket connection
    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting');
      this.ws = null;
    }

    // Reset retry count
    this.retryCount = 0;
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Reset retry count (useful for manual reconnection attempts)
   */
  resetRetryCount(): void {
    this.retryCount = 0;
  }
}

// Export singleton instance
export const messageService = new MessageService();

