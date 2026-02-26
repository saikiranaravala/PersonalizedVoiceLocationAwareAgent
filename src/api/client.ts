/**
 * API Client for Backend Communication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  message: string;
  sessionId?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  intermediate_steps: any[];
}

// REST API Client
export class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async chat(message: string, sessionId: string = 'default'): Promise<ChatResponse> {
    const response = await fetch(`${this.baseURL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, session_id: sessionId }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async getContext() {
    const response = await fetch(`${this.baseURL}/context`);
    return response.json();
  }

  async resetConversation() {
    const response = await fetch(`${this.baseURL}/reset`, {
      method: 'POST',
    });
    return response.json();
  }
}

// WebSocket Client
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private messageHandlers: Map<string, (data: any) => void> = new Map();

  constructor(sessionId: string = 'default') {
    this.sessionId = sessionId;
  }

  connect() {
    const wsURL = API_BASE_URL.replace('http', 'ws');
    this.ws = new WebSocket(`${wsURL}/ws/${this.sessionId}`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.emit('connected', {});
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const handler = this.messageHandlers.get(data.type);
      if (handler) {
        handler(data);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.emit('error', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.emit('disconnected', {});
    };
  }

  send(type: string, data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, ...data }));
    }
  }

  on(eventType: string, handler: (data: any) => void) {
    this.messageHandlers.set(eventType, handler);
  }

  private emit(eventType: string, data: any) {
    const handler = this.messageHandlers.get(eventType);
    if (handler) {
      handler(data);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default new APIClient();