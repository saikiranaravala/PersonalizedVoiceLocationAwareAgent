"""
FastAPI Server for Agentic Assistant
Provides REST and WebSocket APIs for the React frontend
"""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import json
from typing import Optional, List

# Import the agentic assistant
try:
    from agent.core import AgenticAssistant
except ImportError as e:
    print(f"Error importing AgenticAssistant: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt --break-system-packages")
    sys.exit(1)

app = FastAPI(
    title="Agentic Assistant API",
    description="Voice-first AI assistant with location awareness",
    version="1.0.0"
)

# Enable CORS for React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize assistant (singleton)
print("Initializing Agentic Assistant...")
try:
    assistant = AgenticAssistant()
    print("✓ Assistant initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize assistant: {e}")
    print("\nMake sure:")
    print("1. OPENAI_API_KEY is set in config/.env")
    print("2. All dependencies are installed")
    assistant = None

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    success: bool = True
    intermediate_steps: List = []

class StatusResponse(BaseModel):
    status: str
    message: str

# ============================================
# REST API Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "Personalized Agentic Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "context": "/context",
            "reset": "/reset",
            "websocket": "/ws/{session_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if assistant else "unhealthy",
        "service": "agentic-assistant",
        "assistant_initialized": assistant is not None
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process text-based chat request
    
    Example:
    ```json
    {
        "message": "What's the weather?",
        "session_id": "user123"
    }
    ```
    """
    if not assistant:
        raise HTTPException(
            status_code=503, 
            detail="Assistant not initialized. Check server logs."
        )
    
    try:
        result = assistant.process_request(request.message)
        
        return ChatResponse(
            response=result.get("output", ""),
            session_id=request.session_id,
            success=result.get("success", True),
            intermediate_steps=result.get("intermediate_steps", [])
        )
    except Exception as e:
        print(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/context")
async def get_context():
    """Get current conversation context"""
    if not assistant:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    try:
        return {
            "summary": assistant.get_context_summary(),
            "history": assistant.context_manager.get_history(limit=10)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset", response_model=StatusResponse)
async def reset_conversation():
    """Reset conversation history"""
    if not assistant:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    try:
        assistant.reset_conversation()
        return StatusResponse(
            status="success",
            message="Conversation history cleared"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        print(f"✓ Client {session_id} connected via WebSocket")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            print(f"✗ Client {session_id} disconnected")
    
    async def send_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time communication
    
    Example client code (JavaScript):
    ```javascript
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
    if not assistant:
        await websocket.close(code=1011, reason="Assistant not initialized")
        return
    
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            print(f"Received message type: {message_type} from {session_id}")
            
            if message_type == "chat":
                # Process chat message
                user_message = data.get("message", "")
                user_profile = data.get("user_profile")  # Extract user profile
                user_agent = data.get("user_agent")  # Extract user agent
                
                print(f"Processing message: {user_message}")
                print(f"User profile: {user_profile}")
                print(f"User agent: {user_agent}")
                
                # Send "processing" status
                await manager.send_message({
                    "type": "status",
                    "status": "processing",
                    "message": "Processing your request..."
                }, session_id)
                
                try:
                    # Process with assistant (pass user context)
                    result = assistant.process_request(
                        user_message,
                        user_agent=user_agent,
                        user_profile=user_profile
                    )
                    
                    # Extract just the text response (avoid serialization issues)
                    response_text = result.get("output", "")
                    success = result.get("success", True)
                    
                    # Don't send intermediate_steps as they contain non-serializable objects
                    # Send response
                    await manager.send_message({
                        "type": "response",
                        "message": response_text,
                        "success": success
                    }, session_id)
                    
                except Exception as e:
                    print(f"Error processing message: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    await manager.send_message({
                        "type": "error",
                        "message": f"Error processing request: {str(e)}"
                    }, session_id)
            
            elif message_type == "ping":
                # Heartbeat
                await manager.send_message({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                }, session_id)
            
            else:
                await manager.send_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, session_id)
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error for {session_id}: {e}")
        manager.disconnect(session_id)

# ============================================
# Serve Static Files (Production)
# ============================================

# Serve the React build in production
ui_dist = project_root / "ui" / "dist"
if ui_dist.exists():
    app.mount("/", StaticFiles(directory=str(ui_dist), html=True), name="static")
    print(f"✓ Serving UI from {ui_dist}")

# ============================================
# Startup Event
# ============================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("\n" + "="*60)
    print("🚀 Personalized Agentic Assistant API Server")
    print("="*60)
    print(f"Assistant Status: {'✓ Initialized' if assistant else '✗ Failed'}")
    print(f"UI Directory: {'✓ Found' if ui_dist.exists() else '✗ Not built (run in dev mode)'}")
    print("\nAPI Endpoints:")
    print("  - Health Check: http://localhost:8000/health")
    print("  - Chat API: http://localhost:8000/chat")
    print("  - WebSocket: ws://localhost:8000/ws/{session_id}")
    print("\nDevelopment:")
    print("  - Backend: python api_server.py")
    print("  - Frontend: cd ui && npm run dev")
    print("\nProduction:")
    print("  - Build UI: cd ui && npm run build")
    print("  - Start: python api_server.py")
    print("="*60 + "\n")

# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    print("\nStarting server...")
    print("Press Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
