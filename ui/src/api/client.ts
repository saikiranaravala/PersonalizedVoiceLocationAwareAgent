/**
 * API Client for Agentic Assistant Backend
 * Handles WebSocket and REST communication
 */

export interface Message {
  type: 'chat' | 'status' | 'response' | 'error' | 'pong';
  message?: string;
  status?: 'processing' | 'listening' | 'speaking';
  success?: boolean;
  intermediate_steps?: any[];
  timestamp?: number;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  success: boolean;
  intermediate_steps: any[];
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private hasConnectedOnce = false;
  
  // Event handlers
  public onMessage: (message: Message) => void = () => {};
  public onOpen: () => void = () => {};
  public onClose: () => void = () => {};
  public onError: (error: Event) => void = () => {};

  constructor(url: string = 'ws://localhost:8000', sessionId?: string) {
    this.url = url;
    this.sessionId = sessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    try {
      const wsUrl = `${this.url}/ws/${this.sessionId}`;
      console.log(`[WebSocket] Connecting to ${wsUrl}...`);
      
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[WebSocket] Connected successfully');
        this.reconnectAttempts = 0;
        this.hasConnectedOnce = true;
        this.onOpen();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: Message = JSON.parse(event.data);
          console.log('[WebSocket] Received:', message);
          this.onMessage(message);
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
        }
      };

      this.ws.onerror = (error) => {
        // Only log errors if we've successfully connected before
        // This suppresses expected errors during initial connection attempts
        if (this.hasConnectedOnce) {
          console.error('[WebSocket] Error:', error);
          this.onError(error);
        } else {
          // First connection - just log info, not error
          console.log('[WebSocket] Initial connection attempt in progress...');
        }
      };

      this.ws.onclose = () => {
        console.log('[WebSocket] Connection closed');
        this.onClose();
        this.attemptReconnect();
      };

    } catch (error) {
      console.error('[WebSocket] Connection failed:', error);
      this.attemptReconnect();
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Send a chat message
   */
  sendMessage(message: string): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('[WebSocket] Connection not open');
      throw new Error('WebSocket not connected');
    }

    const payload: Message = {
      type: 'chat',
      message: message,
      timestamp: Date.now()
    };

    console.log('[WebSocket] Sending:', payload);
    this.ws.send(JSON.stringify(payload));
  }

  /**
   * Send a ping to keep connection alive
   */
  ping(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return;
    }

    this.ws.send(JSON.stringify({
      type: 'ping',
      timestamp: Date.now()
    }));
  }

  /**
   * Close the WebSocket connection
   */
  disconnect(): void {
    if (this.ws) {
      console.log('[WebSocket] Disconnecting...');
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

/**
 * REST API Client
 */
export class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }

  /**
   * Send a chat message via REST
   */
  async chat(message: string, sessionId?: string): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId || 'default'
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get conversation context
   */
  async getContext(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/context`);
    return response.json();
  }

  /**
   * Reset conversation
   */
  async reset(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/reset`, {
      method: 'POST'
    });
    return response.json();
  }
}

// Export singleton instances
export const apiClient = new APIClient();
