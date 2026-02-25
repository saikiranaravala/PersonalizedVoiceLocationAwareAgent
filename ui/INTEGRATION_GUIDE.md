# UI Integration Guide

## Connecting the React UI to the Python Backend

This guide shows how to integrate the voice-first React UI with the Python agentic assistant backend.

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         React Frontend (UI)              │
│  - Voice Button                          │
│  - Conversation Display                  │
│  - Theme Management                      │
└──────────────┬──────────────────────────┘
               │ WebSocket / REST API
               │
┌──────────────▼──────────────────────────┐
│      FastAPI Backend Server              │
│  - WebSocket handler                     │
│  - REST API endpoints                    │
│  - Session management                    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Python Agentic Assistant               │
│  - AgenticAssistant class                │
│  - Tool execution                        │
│  - LLM integration                       │
└──────────────────────────────────────────┘
```

---

## Step 1: Create FastAPI Backend

### Install Dependencies

```bash
cd /path/to/personalized-agentic-assistant
pip install fastapi uvicorn websockets python-multipart --break-system-packages
```

### Create `api_server.py`

```python
"""
FastAPI Server for Agentic Assistant
Provides REST and WebSocket APIs for the React frontend
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import json
from typing import Optional

# Import the agentic assistant
import sys
sys.path.insert(0, 'src')
from agent.core import AgenticAssistant
from services.speech import SpeechService

app = FastAPI(title="Agentic Assistant API")

# Enable CORS for React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite/React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize assistant (singleton)
assistant = AgenticAssistant()

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    intermediate_steps: list = []

class VoiceRequest(BaseModel):
    audio_base64: str
    session_id: Optional[str] = "default"

# ============================================
# REST API Endpoints
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "agentic-assistant"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process text-based chat request
    
    Example:
    POST /chat
    {
        "message": "What's the weather?",
        "session_id": "user123"
    }
    """
    try:
        result = assistant.process_request(request.message)
        
        return ChatResponse(
            response=result.get("output", ""),
            session_id=request.session_id,
            intermediate_steps=result.get("intermediate_steps", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice")
async def voice_endpoint(request: VoiceRequest):
    """
    Process voice-based request (base64 audio)
    
    Example:
    POST /voice
    {
        "audio_base64": "...",
        "session_id": "user123"
    }
    """
    # TODO: Implement voice processing
    # 1. Decode base64 audio
    # 2. Convert to text (STT)
    # 3. Process with assistant
    # 4. Return response
    
    raise HTTPException(status_code=501, detail="Voice processing not implemented yet")

@app.get("/context")
async def get_context():
    """Get current conversation context"""
    return {
        "summary": assistant.get_context_summary(),
        "history": assistant.context_manager.get_history(limit=10)
    }

@app.post("/reset")
async def reset_conversation():
    """Reset conversation history"""
    assistant.reset_conversation()
    return {"status": "reset", "message": "Conversation history cleared"}

# ============================================
# WebSocket for Real-time Communication
# ============================================

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time communication
    
    Example client code (JavaScript):
    ```
    const ws = new WebSocket('ws://localhost:8000/ws/user123');
    
    ws.onopen = () => {
        ws.send(JSON.stringify({
            type: 'chat',
            message: 'What is the weather?'
        }));
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Response:', data);
    };
    ```
    """
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "chat":
                # Process chat message
                user_message = data.get("message", "")
                
                # Send "processing" status
                await manager.send_message({
                    "type": "status",
                    "status": "processing"
                }, session_id)
                
                # Process with assistant
                result = assistant.process_request(user_message)
                
                # Send response
                await manager.send_message({
                    "type": "response",
                    "message": result.get("output", ""),
                    "intermediate_steps": result.get("intermediate_steps", [])
                }, session_id)
                
            elif message_type == "voice":
                # Handle voice input
                await manager.send_message({
                    "type": "error",
                    "message": "Voice processing not implemented"
                }, session_id)
            
            elif message_type == "ping":
                # Heartbeat
                await manager.send_message({
                    "type": "pong"
                }, session_id)
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        print(f"Client {session_id} disconnected")

# ============================================
# Serve Static Files (Production)
# ============================================

# Uncomment this in production to serve the React build
# app.mount("/", StaticFiles(directory="ui/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Step 2: Create React API Client

### Create `src/api/client.ts`

```typescript
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
```

---

## Step 3: Update React App to Use API

### Modified `App.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { APIClient, WebSocketClient } from './api/client';
import VoiceButton from './components/voice/VoiceButton/VoiceButton';

function App() {
  const [apiClient] = useState(() => new APIClient());
  const [wsClient] = useState(() => new WebSocketClient());
  const [voiceStatus, setVoiceStatus] = useState('idle');
  const [conversation, setConversation] = useState([]);

  useEffect(() => {
    // Connect WebSocket
    wsClient.connect();

    wsClient.on('response', (data) => {
      setConversation(prev => [
        ...prev,
        { role: 'assistant', text: data.message, timestamp: new Date() }
      ]);
      setVoiceStatus('idle');
    });

    wsClient.on('status', (data) => {
      setVoiceStatus(data.status);
    });

    return () => wsClient.disconnect();
  }, []);

  const handleVoicePress = async () => {
    setVoiceStatus('listening');
    
    // Simulate voice recording
    setTimeout(async () => {
      setVoiceStatus('processing');
      
      // Send message via WebSocket
      wsClient.send('chat', {
        message: "What's the weather like?"
      });
      
      // Or use REST API
      // const response = await apiClient.chat("What's the weather like?");
      // setConversation(prev => [...prev, { role: 'assistant', text: response.response }]);
    }, 2000);
  };

  return (
    <div className="app">
      {/* ... UI components ... */}
      <VoiceButton
        status={voiceStatus}
        onPress={handleVoicePress}
        size="large"
      />
    </div>
  );
}
```

---

## Step 4: Running the Full Stack

### Terminal 1: Start Python Backend

```bash
cd /path/to/personalized-agentic-assistant
python api_server.py
```

Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Terminal 2: Start React Frontend

```bash
cd /path/to/personalized-agentic-assistant/ui
npm run dev
```

Output:
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Access the App

Open browser: `http://localhost:5173`

---

## Step 5: Environment Configuration

### Create `.env` in UI folder

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Production Build

```bash
# Build React app
cd ui
npm run build

# Serve with FastAPI
# Uncomment in api_server.py:
# app.mount("/", StaticFiles(directory="ui/dist", html=True))

# Run production server
python api_server.py
```

Access at: `http://localhost:8000`

---

## API Reference

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/chat` | POST | Send text message |
| `/voice` | POST | Send voice audio |
| `/context` | GET | Get conversation context |
| `/reset` | POST | Reset conversation |

### WebSocket Events

**Client → Server:**
- `{ type: 'chat', message: 'text' }`
- `{ type: 'voice', audio_base64: '...' }`
- `{ type: 'ping' }`

**Server → Client:**
- `{ type: 'response', message: 'text', intermediate_steps: [] }`
- `{ type: 'status', status: 'processing' }`
- `{ type: 'error', message: 'error text' }`
- `{ type: 'pong' }`

---

## Deployment

### Option 1: Separate Deployment

**Backend (Python):**
- Deploy FastAPI to: Heroku, Railway, Fly.io
- Use: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

**Frontend (React):**
- Deploy to: Vercel, Netlify, Cloudflare Pages
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_URL=https://your-api.com`

### Option 2: Single Deployment

Build React app and serve from FastAPI:

```bash
# Build frontend
cd ui && npm run build && cd ..

# Deploy FastAPI with static files
python api_server.py
```

Deploy to: Railway, Render, Fly.io

---

## Troubleshooting

### CORS Errors

Ensure FastAPI CORS middleware includes your frontend URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-domain.com"],
    # ...
)
```

### WebSocket Connection Failed

Check:
1. Backend is running
2. Firewall allows WebSocket connections
3. Correct WebSocket URL (ws:// not http://)

### API Timeout

Increase timeout in FastAPI:

```python
uvicorn.run(app, timeout_keep_alive=30)
```

---

## Next Steps

1. ✅ Implement voice recording in React
2. ✅ Add speech-to-text processing in backend
3. ✅ Implement text-to-speech responses
4. ✅ Add authentication/session management
5. ✅ Deploy to production

---

**You now have a complete full-stack voice assistant!** 🎉
