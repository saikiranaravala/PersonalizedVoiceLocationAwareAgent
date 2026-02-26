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