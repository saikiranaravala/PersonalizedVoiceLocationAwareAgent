# 🎤 Voice-First AI Assistant - Complete Documentation

**A production-ready, voice-first AI assistant with Python backend, React frontend, and seamless voice interaction.**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Quick Start](#quick-start)
5. [Voice Control Guide](#voice-control-guide)
6. [Backend Setup](#backend-setup)
7. [Frontend Setup](#frontend-setup)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)
10. [API Documentation](#api-documentation)
11. [Development Guide](#development-guide)
12. [Deployment](#deployment)

---

## 🎯 Overview

This is a **fully functional voice-first AI assistant** that combines:
- **Voice Recognition** using Web Speech API
- **Natural Language Processing** via OpenRouter/OpenAI
- **Voice Synthesis** for spoken responses
- **Real-time Communication** through WebSocket
- **Location-Aware Tools** (Weather, Uber, Zomato)
- **Professional UI** with 5 themes and accessibility features

### Key Capabilities

- 🎤 **Voice Interaction** - Push-to-talk, manual stop, or auto-timeout
- 💬 **Text Chat** - Full conversation interface
- 🔧 **Extensible Tools** - Weather, ride-hailing, restaurant search
- 🎨 **Beautiful UI** - 5 themes, responsive design, WCAG AAA compliant
- 📊 **Monitoring** - LangSmith integration for debugging
- 🔄 **Real-time** - WebSocket for instant responses

---

## ✨ Features

### Voice Features
- ✅ **Push-to-Talk** - Hold button to record, release to send
- ✅ **Manual Stop** - Click button, speak, then click "Stop & Send"
- ✅ **Auto-Timeout** - 10-second safety timeout
- ✅ **Visual Feedback** - Clear on-screen instructions
- ✅ **Speech Synthesis** - Responses are spoken aloud
- ✅ **Confidence Scores** - Speech recognition quality monitoring
- ✅ **Error Recovery** - Automatic retry and reconnection

### Backend Features
- ✅ **FastAPI** - High-performance async Python backend
- ✅ **LangChain Integration** - Agent with tool calling
- ✅ **OpenRouter/OpenAI** - Multiple LLM support
- ✅ **WebSocket** - Real-time bidirectional communication
- ✅ **CORS Enabled** - Cross-origin support
- ✅ **Health Checks** - Monitoring endpoints
- ✅ **Extensible Tools** - Easy to add new capabilities

### Frontend Features
- ✅ **React + TypeScript** - Type-safe modern frontend
- ✅ **Vite** - Lightning-fast development
- ✅ **5 Themes** - Modern, Classic, Playful, Professional, Minimal
- ✅ **Responsive** - Mobile, tablet, desktop optimized
- ✅ **Accessible** - WCAG AAA compliant
- ✅ **Connection Management** - Smart reconnection logic
- ✅ **Error Handling** - User-friendly error messages

### Tool Integrations
- 🌤️ **Weather** - Location-based weather information
- 🚗 **Uber** - Ride estimates and booking
- 🍽️ **Zomato** - Restaurant search and details
- ➕ **Extensible** - Easy to add more tools

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │            React Frontend (Vite)                  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Voice Recognition (Web Speech API)        │  │  │
│  │  │  - Microphone input                        │  │  │
│  │  │  - Speech to text                          │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  UI Components                             │  │  │
│  │  │  - Voice button (push-to-talk)             │  │  │
│  │  │  - Conversation display                    │  │  │
│  │  │  - Theme selector                          │  │  │
│  │  │  - Connection status                       │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  WebSocket Client                          │  │  │
│  │  │  - Real-time messaging                     │  │  │
│  │  │  - Auto-reconnection                       │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Speech Synthesis                          │  │  │
│  │  │  - Text to speech                          │  │  │
│  │  │  - Voice playback                          │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                    WebSocket/HTTP
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Python Backend (FastAPI)                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  WebSocket Manager                                │  │
│  │  - Connection handling                            │  │
│  │  - Session management                             │  │
│  │  - Message routing                                │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  LangChain Agent                                  │  │
│  │  - Message processing                             │  │
│  │  - Tool selection                                 │  │
│  │  - Response generation                            │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Tools                                            │  │
│  │  ┌────────────┬─────────────┬──────────────┐    │  │
│  │  │  Weather   │    Uber     │   Zomato     │    │  │
│  │  │  Tool      │    Tool     │   Tool       │    │  │
│  │  └────────────┴─────────────┴──────────────┘    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                    API Calls
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  External Services                      │
│  ┌────────────┬─────────────┬──────────────────────┐  │
│  │ OpenRouter │  Weather    │  Uber / Zomato APIs  │  │
│  │ / OpenAI   │  APIs       │                       │  │
│  └────────────┴─────────────┴──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

**Voice Input Flow:**
```
User speaks → Web Speech API → Transcript
    ↓
WebSocket → Backend receives
    ↓
LangChain Agent processes → Calls tools if needed
    ↓
Response generated → WebSocket → Frontend receives
    ↓
Display in UI + Speak via Speech Synthesis
```

**Text Input Flow:**
```
User types → Send via WebSocket → Backend processes
    ↓
LangChain Agent → Response → WebSocket → Frontend
    ↓
Display in conversation
```

---

## 🚀 Quick Start

### Prerequisites

**Backend:**
- Python 3.8+
- pip package manager

**Frontend:**
- Node.js 16+
- npm or yarn

**API Keys:**
- OpenRouter API key OR OpenAI API key
- (Optional) Weather API key
- (Optional) Uber API credentials
- (Optional) Zomato API key

### Installation

#### 1. Extract Package
```bash
tar -xzf personalized-agentic-assistant-no-refresh-errors.tar.gz
cd personalized-agentic-assistant
```

#### 2. Setup Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Or with break-system-packages flag if needed
pip install -r requirements.txt --break-system-packages

# Set environment variables
export OPENROUTER_API_KEY="your_key_here"
export USER_LOCATION="Erie, Pennsylvania, US"

# Or create .env file
echo "OPENROUTER_API_KEY=your_key_here" > .env
echo "USER_LOCATION=Erie, Pennsylvania, US" >> .env
```

#### 3. Setup Frontend
```bash
cd ui
npm install
```

#### 4. Start Backend
```bash
# From project root
python api_server.py

# Should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# Assistant initialized successfully
```

#### 5. Start Frontend
```bash
# From ui/ directory
npm run dev

# Should see:
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
```

#### 6. Open Browser
```
Navigate to: http://localhost:5173
```

**You should see:**
- Brief blue "Connecting..." banner
- Green dot next to title (connected)
- Voice button ready to use

---

## 🎤 Voice Control Guide

### Three Ways to Use Voice

#### 1. Push-to-Talk (Recommended) 🎯

**Desktop:**
```
1. HOLD the microphone button (mouse down)
2. Speak your message
3. RELEASE the button (mouse up)
4. Message is sent automatically
```

**Mobile:**
```
1. TOUCH and HOLD the microphone button
2. Speak your message
3. LIFT your finger
4. Message is sent automatically
```

**Best for:** Quick commands (<5 seconds)

**Example:**
```
Hold button → "What's the weather?" → Release → Done!
```

#### 2. Manual Stop Button 🛑

**How to use:**
```
1. Click the microphone button (single click)
2. See "Listening... Release when done" text
3. "Stop & Send" button appears below microphone
4. Speak your full message
5. Click "Stop & Send" when finished
```

**Best for:** Longer messages, composing thoughts

**Example:**
```
Click → "Find me restaurants near me that serve Italian food 
and have outdoor seating" → Click "Stop & Send" → Done!
```

#### 3. Auto-Timeout ⏰

**How it works:**
```
1. Click microphone button
2. Speak your message
3. After 10 seconds of no speech, automatically stops
4. Message is sent
```

**Best for:** Safety net if you forget to stop

### Visual States

**Idle (Ready):**
```
┌─────────────────────────┐
│  Hold to talk, release  │
│       to send           │
├─────────────────────────┤
│         🎤              │
│      (Blue)             │
└─────────────────────────┘
```

**Listening (Recording):**
```
┌─────────────────────────┐
│  Listening... Release   │
│      when done          │
├─────────────────────────┤
│         🎤              │
│   (Orange, pulsing)     │
│     ≈≈≈≈≈≈≈≈≈≈         │
├─────────────────────────┤
│    [Stop & Send]        │
└─────────────────────────┘
```

**Processing:**
```
┌─────────────────────────┐
│  Processing your        │
│     request...          │
├─────────────────────────┤
│         🎤              │
│    (Blue, spinning)     │
└─────────────────────────┘
```

**Speaking:**
```
┌─────────────────────────┐
│  Speaking response...   │
├─────────────────────────┤
│         🔊              │
│   (Green, glowing)      │
└─────────────────────────┘
```

### Keyboard Accessibility

**Push-to-Talk:**
```
1. Tab to microphone button
2. HOLD Space or Enter key
3. Speak your message
4. RELEASE key
5. Message sent
```

**Manual Stop:**
```
1. Tab to microphone button
2. Press Space or Enter (single press)
3. Speak your message
4. Tab to "Stop & Send" button
5. Press Space or Enter
```

---

## 🔧 Backend Setup

### File Structure

```
personalized-agentic-assistant/
├── api_server.py              # Main FastAPI server
├── assistant.py               # LangChain agent logic
├── tools/                     # Tool implementations
│   ├── __init__.py
│   ├── weather.py            # Weather tool
│   ├── uber.py               # Uber tool
│   └── zomato.py             # Zomato tool
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```

### Environment Variables

Create a `.env` file:

```bash
# Required: OpenRouter OR OpenAI
OPENROUTER_API_KEY=your_openrouter_key
# OR
OPENAI_API_KEY=your_openai_key

# Required: User location for context
USER_LOCATION=Erie, Pennsylvania, US

# Optional: LangSmith monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=voice-assistant

# Optional: Tool API keys
WEATHER_API_KEY=your_weather_key
UBER_CLIENT_ID=your_uber_id
UBER_CLIENT_SECRET=your_uber_secret
ZOMATO_API_KEY=your_zomato_key
```

### Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Or manually install key packages
pip install fastapi uvicorn websockets
pip install langchain langchain-openai
pip install python-dotenv pydantic
```

### Running the Backend

**Standard:**
```bash
python api_server.py
```

**With Auto-Reload (Development):**
```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

**Production (with workers):**
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Endpoints

**Health Check:**
```bash
GET http://localhost:8000/health

Response:
{
  "status": "healthy",
  "assistant_initialized": true
}
```

**REST Chat:**
```bash
POST http://localhost:8000/chat
Content-Type: application/json

{
  "message": "What's the weather?"
}

Response:
{
  "response": "Current weather in Erie, PA is...",
  "success": true
}
```

**WebSocket:**
```javascript
ws://localhost:8000/ws/{session_id}

Send:
{
  "type": "chat",
  "message": "Hello"
}

Receive:
{
  "type": "response",
  "message": "Hi! How can I help?",
  "success": true
}
```

---

## 💻 Frontend Setup

### File Structure

```
ui/
├── src/
│   ├── App.tsx                    # Main app component
│   ├── App.css                    # Global styles
│   ├── hooks/
│   │   └── useVoiceAssistant.ts   # Voice logic hook
│   ├── components/
│   │   ├── voice/
│   │   │   └── VoiceButton/       # Voice button component
│   │   ├── Button/                # Reusable button
│   │   └── ui/                    # UI primitives
│   ├── api/
│   │   └── client.ts              # WebSocket & REST client
│   └── themes/
│       └── themes.ts              # Theme definitions
├── index.html
├── package.json
└── vite.config.ts
```

### Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

### Running the Frontend

**Development:**
```bash
cd ui
npm run dev

# Opens on http://localhost:5173
```

**Build for Production:**
```bash
npm run build

# Output in dist/
```

**Preview Production Build:**
```bash
npm run preview
```

### Configuration

**vite.config.ts:**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  }
})
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Voice Button Stuck on "Listening..."

**Symptoms:**
- Button shows "Listening..." indefinitely
- No timeout after 10 seconds

**Causes:**
- Speech recognition not starting properly
- Microphone permission denied

**Solutions:**
```bash
# Check browser console for errors
F12 → Console → Look for red errors

# Test microphone
Open: ui/test-speech-recognition.html
Click "Start Listening"

# Grant microphone permission
Chrome: Settings → Privacy → Site Settings → Microphone → Allow localhost
```

#### 2. "Cannot Send - Not Connected"

**Symptoms:**
- Voice recognition works (shows confidence)
- But error: "Cannot send - not connected"

**Causes:**
- WebSocket not actually connected
- Backend not running

**Solutions:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check WebSocket connection
Open: ui/websocket-debugger.html
Click "Connect"
Should show: "CONNECTED ✓"

# Restart both backend and frontend
python api_server.py
cd ui && npm run dev
```

#### 3. Page Refresh Shows Errors

**Symptoms:**
- Red errors appear briefly on page load
- Then disappears and works fine

**Status:** ✅ Fixed in latest version

**What was fixed:**
- Added "Connecting" state (blue banner)
- Suppressed initial connection errors
- 2-second grace period before showing errors

**Expected behavior now:**
- Blue "Connecting..." banner appears briefly
- Smoothly transitions to connected state
- No red errors during normal connection

#### 4. Backend Not Responding

**Symptoms:**
- Quick action buttons don't work
- No responses appear

**Causes:**
- Backend crashed
- Wrong port
- Firewall blocking

**Solutions:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check backend logs
# Look for errors in terminal where python api_server.py runs

# Try different port
uvicorn api_server:app --port 8001

# Update frontend to match
# Edit ui/src/hooks/useVoiceAssistant.ts
# Change: backendUrl = 'ws://localhost:8001'

# Check firewall (Windows)
netsh advfirewall firewall add rule name="Allow 8000" dir=in action=allow protocol=TCP localport=8000
```

#### 5. Microphone Not Working

**Symptoms:**
- Voice button works but no speech detected
- Always timeout after 10 seconds

**Causes:**
- Wrong microphone selected
- Microphone muted
- Browser permission denied

**Solutions:**
```bash
# Test microphone in Windows
Settings → System → Sound → Input → Test microphone
Speak - bars should move

# Check browser microphone permission
Chrome: Click lock icon in address bar → Site settings → Microphone → Allow

# Select correct microphone
Windows: Right-click speaker icon → Sounds → Recording → Set default

# Test with standalone tool
Open: ui/test-speech-recognition.html
Should detect speech
```

#### 6. No Response from LLM

**Symptoms:**
- Message sent successfully
- Processing forever
- No response appears

**Causes:**
- Invalid API key
- API rate limit
- Network issue

**Solutions:**
```bash
# Check API key
echo $OPENROUTER_API_KEY
# Should show your key

# Test API directly
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"

# Check backend logs
# Look for API errors

# Try different model
# Edit assistant.py
# Change model to "anthropic/claude-3-sonnet"
```

---

## ⚙️ Advanced Configuration

### Backend Configuration

**api_server.py - Main settings:**

```python
# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Add your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket timeout
WEBSOCKET_TIMEOUT = 300  # 5 minutes

# Server settings
if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",      # Bind to all interfaces
        port=8000,           # Port number
        reload=True,         # Auto-reload on changes
        log_level="info"     # Logging level
    )
```

**assistant.py - Agent settings:**

```python
# LLM configuration
llm = ChatOpenAI(
    model="anthropic/claude-3-5-sonnet",  # Model to use
    temperature=0.7,                       # Creativity (0-1)
    openai_api_key=api_key,
    openai_api_base=base_url,
    max_tokens=1000                        # Response length
)

# Agent configuration
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,           # Debug logging
    max_iterations=5,       # Max tool calls
    handle_parsing_errors=True
)
```

### Frontend Configuration

**useVoiceAssistant.ts - Options:**

```typescript
const {
  status,
  conversation,
  isConnected,
  // ... other returns
} = useVoiceAssistant({
  backendUrl: 'ws://localhost:8000',  // Backend WebSocket URL
  sessionId: 'custom-session-id',     // Optional custom session
  autoConnect: true,                   // Auto-connect on mount
  enableSpeechRecognition: true,       // Enable voice input
  enableSpeechSynthesis: true,         // Enable voice output
});
```

**Speech Recognition Settings:**

```typescript
// In useVoiceAssistant.ts
recognition.continuous = false;        // Don't keep listening
recognition.interimResults = false;    // Only final results
recognition.maxAlternatives = 1;       // One transcript
recognition.lang = 'en-US';           // Language

// Timeout duration
const LISTENING_TIMEOUT = 10000;      // 10 seconds
```

**Speech Synthesis Settings:**

```typescript
// In useVoiceAssistant.ts
utterance.rate = 1.0;      // Speed (0.1 - 10)
utterance.pitch = 1.0;     // Pitch (0 - 2)
utterance.volume = 1.0;    // Volume (0 - 1)
utterance.lang = 'en-US';  // Language
```

### Theme Customization

**themes/themes.ts - Add new theme:**

```typescript
export const themes: Record<string, Theme> = {
  // ... existing themes
  
  myCustomTheme: {
    name: 'My Theme',
    colors: {
      primary: {
        50: '#fff5f7',
        // ... other shades
        500: '#ff1744',
      },
      background: '#fafafa',
      text: {
        primary: '#1a1a1a',
        secondary: '#666666',
      },
      // ... other colors
    },
    fonts: {
      body: 'Inter, system-ui, sans-serif',
      heading: 'Inter, system-ui, sans-serif',
      mono: 'Fira Code, monospace',
    },
    // ... other settings
  },
};
```

### Adding New Tools

**Create tool file: `tools/my_tool.py`**

```python
from langchain.tools import Tool
from typing import Optional

def my_tool_function(query: str, user_location: Optional[str] = None) -> str:
    """
    Description of what the tool does.
    
    Args:
        query: The user's query
        user_location: User's location if available
        
    Returns:
        str: The result
    """
    # Your tool logic here
    result = f"Processed: {query}"
    return result

def get_my_tool(user_location: Optional[str] = None) -> Tool:
    """Get the tool instance."""
    return Tool(
        name="my_tool",
        description="When to use this tool - be specific",
        func=lambda query: my_tool_function(query, user_location)
    )
```

**Register tool in `assistant.py`:**

```python
from tools.my_tool import get_my_tool

# In initialize_assistant function
tools = [
    get_weather_tool(user_location),
    get_uber_tool(user_location),
    get_zomato_tool(user_location),
    get_my_tool(user_location),  # Add your tool
]
```

---

## 📚 API Documentation

### WebSocket Protocol

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{session_id}');
```

**Message Types:**

#### 1. Chat Message (Client → Server)
```json
{
  "type": "chat",
  "message": "What's the weather like?",
  "timestamp": 1234567890
}
```

#### 2. Status Update (Server → Client)
```json
{
  "type": "status",
  "status": "processing",
  "timestamp": 1234567890
}
```

#### 3. Response (Server → Client)
```json
{
  "type": "response",
  "message": "The current weather in Erie, PA is...",
  "success": true,
  "timestamp": 1234567890
}
```

#### 4. Error (Server → Client)
```json
{
  "type": "error",
  "message": "Failed to process request",
  "timestamp": 1234567890
}
```

#### 5. Ping/Pong (Keepalive)
```json
{
  "type": "ping",
  "timestamp": 1234567890
}
```

### REST API

**POST /chat**

Request:
```json
{
  "message": "Find Italian restaurants near me"
}
```

Response:
```json
{
  "response": "Here are some Italian restaurants...",
  "success": true
}
```

**GET /health**

Response:
```json
{
  "status": "healthy",
  "assistant_initialized": true
}
```

---

## 👨‍💻 Development Guide

### Project Structure

```
personalized-agentic-assistant/
├── api_server.py                 # FastAPI server
├── assistant.py                  # LangChain agent
├── requirements.txt              # Python dependencies
├── tools/                        # Tool implementations
│   ├── __init__.py
│   ├── weather.py
│   ├── uber.py
│   └── zomato.py
├── ui/                           # React frontend
│   ├── src/
│   │   ├── App.tsx              # Main component
│   │   ├── hooks/
│   │   │   └── useVoiceAssistant.ts
│   │   ├── components/
│   │   │   ├── voice/
│   │   │   │   └── VoiceButton/
│   │   │   └── Button/
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── themes/
│   │       └── themes.ts
│   ├── package.json
│   └── vite.config.ts
├── test_backend.py              # Backend tests
└── docs/                        # Documentation
    ├── CLAUDE.md                # This file
    ├── QUICK_FIX_GUIDE.md
    ├── PUSH_TO_TALK_GUIDE.md
    ├── VOICE_BACKEND_FIX.md
    └── CONNECTION_STATE_FIX.md
```

### Development Workflow

**1. Setup Development Environment:**

```bash
# Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ui
npm install
```

**2. Start Development Servers:**

```bash
# Terminal 1: Backend with auto-reload
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend with hot-reload
cd ui
npm run dev
```

**3. Make Changes:**

- Backend changes auto-reload with uvicorn --reload
- Frontend changes hot-reload with Vite HMR
- Test changes immediately in browser

**4. Test:**

```bash
# Test backend
python test_backend.py

# Test frontend
npm run test  # If tests configured

# Manual testing
Open: http://localhost:5173
Use voice and chat features
```

### Code Style

**Python (PEP 8):**
```python
# Use type hints
def process_message(message: str, session_id: str) -> Dict[str, Any]:
    """
    Process incoming message.
    
    Args:
        message: User's message
        session_id: Session identifier
        
    Returns:
        Response dictionary
    """
    # Implementation
    pass

# Use descriptive names
user_location = "Erie, PA"
api_response = call_external_api()
```

**TypeScript:**
```typescript
// Use interfaces
interface VoiceStatus {
  status: 'idle' | 'listening' | 'processing' | 'speaking' | 'error';
  transcript?: string;
}

// Use arrow functions
const handleVoiceInput = (transcript: string): void => {
  // Implementation
};

// Use descriptive names
const isConnected = true;
const voiceAssistant = useVoiceAssistant();
```

### Testing

**Backend Tests:**

Create `tests/test_assistant.py`:
```python
import pytest
from assistant import initialize_assistant

def test_assistant_initialization():
    """Test that assistant initializes successfully."""
    assistant = initialize_assistant()
    assert assistant is not None

def test_assistant_response():
    """Test that assistant generates responses."""
    assistant = initialize_assistant()
    response = assistant.run("Hello")
    assert len(response) > 0
    assert isinstance(response, str)
```

Run tests:
```bash
pytest tests/
```

**Frontend Tests:**

Create `ui/src/hooks/__tests__/useVoiceAssistant.test.ts`:
```typescript
import { renderHook } from '@testing-library/react';
import { useVoiceAssistant } from '../useVoiceAssistant';

describe('useVoiceAssistant', () => {
  it('should initialize with idle status', () => {
    const { result } = renderHook(() => useVoiceAssistant());
    expect(result.current.status).toBe('idle');
  });

  it('should start listening when requested', () => {
    const { result } = renderHook(() => useVoiceAssistant());
    result.current.startListening();
    expect(result.current.status).toBe('listening');
  });
});
```

### Debugging

**Backend Debugging:**

```python
# Add print statements
print(f"[DEBUG] Received message: {message}")

# Use pdb debugger
import pdb; pdb.set_trace()

# Check logs
tail -f logs/api_server.log
```

**Frontend Debugging:**

```typescript
// Console logging
console.log('[DEBUG] Voice status:', status);

// React DevTools
// Install: https://react.dev/learn/react-developer-tools

// Network tab
// F12 → Network → WS (WebSocket messages)
```

---

## 🚀 Deployment

### Backend Deployment

**Production Server (Linux):**

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Setup application
cd /opt/voice-assistant
pip3 install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/voice-assistant.service
```

**systemd service file:**
```ini
[Unit]
Description=Voice Assistant Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/voice-assistant
Environment="OPENROUTER_API_KEY=your_key"
Environment="USER_LOCATION=Erie, Pennsylvania, US"
ExecStart=/usr/bin/python3 -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant
sudo systemctl start voice-assistant
sudo systemctl status voice-assistant
```

**Nginx reverse proxy:**

```nginx
server {
    listen 80;
    server_name voice-assistant.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Frontend Deployment

**Build for production:**
```bash
cd ui
npm run build
# Output in dist/
```

**Deploy to Nginx:**
```bash
# Copy build files
sudo cp -r dist/* /var/www/voice-assistant/

# Nginx config
sudo nano /etc/nginx/sites-available/voice-assistant
```

**Nginx frontend config:**
```nginx
server {
    listen 80;
    server_name app.voice-assistant.example.com;
    root /var/www/voice-assistant;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**Enable and restart:**
```bash
sudo ln -s /etc/nginx/sites-available/voice-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Docker Deployment

**Dockerfile.backend:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Dockerfile.frontend:**
```dockerfile
FROM node:18 AS builder

WORKDIR /app
COPY ui/package*.json ./
RUN npm ci

COPY ui/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - USER_LOCATION=${USER_LOCATION}
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

**Deploy with Docker:**
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 📊 Monitoring & Logging

### LangSmith Integration

**Setup:**
```bash
# Add to .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=voice-assistant
```

**View traces:**
```
https://smith.langchain.com/
```

### Application Logs

**Backend logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Application started")
```

**Frontend logging:**
```typescript
// Centralized logger
class Logger {
  static info(message: string, ...args: any[]) {
    console.log(`[INFO] ${message}`, ...args);
  }
  
  static error(message: string, ...args: any[]) {
    console.error(`[ERROR] ${message}`, ...args);
  }
}

// Usage
Logger.info('WebSocket connected');
Logger.error('Connection failed', error);
```

---

## 🔒 Security

### API Key Management

**Never commit API keys:**
```bash
# Add to .gitignore
.env
.env.local
*.key
```

**Use environment variables:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENROUTER_API_KEY')
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not set")
```

### CORS Configuration

**Restrict origins in production:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.yourdomain.com",  # Your production domain
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting

**Add rate limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, message: ChatMessage):
    # Implementation
    pass
```

---

## 📖 Additional Resources

### Documentation Files

- **QUICK_FIX_GUIDE.md** - Troubleshooting for all issues
- **PUSH_TO_TALK_GUIDE.md** - Complete voice control guide
- **VOICE_BACKEND_FIX.md** - Voice-to-backend connection fix
- **CONNECTION_STATE_FIX.md** - Page refresh error fix
- **WEBSOCKET_TROUBLESHOOTING.md** - WebSocket debugging

### Testing Tools

- **ui/test-speech-recognition.html** - Standalone speech test
- **ui/websocket-debugger.html** - WebSocket connection tester
- **test_backend.py** - Backend test suite

### External Documentation

- **LangChain:** https://python.langchain.com/docs/
- **FastAPI:** https://fastapi.tiangolo.com/
- **React:** https://react.dev/
- **Web Speech API:** https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

---

## 🎉 Summary

This voice-first AI assistant provides:

✅ **Complete voice interaction** - Push-to-talk, manual stop, auto-timeout
✅ **Real-time communication** - WebSocket for instant responses
✅ **Extensible architecture** - Easy to add new tools and features
✅ **Professional UI** - 5 themes, responsive, accessible
✅ **Production-ready** - Error handling, reconnection, monitoring
✅ **Well-documented** - Comprehensive guides and examples

### Quick Commands

```bash
# Start everything
python api_server.py &
cd ui && npm run dev

# Test
curl http://localhost:8000/health
open http://localhost:5173

# Debug
python test_backend.py
open ui/websocket-debugger.html
```

### Getting Help

1. Check documentation files in the package
2. Review console logs (F12 in browser)
3. Test with diagnostic tools
4. Verify API keys and configuration

---

**Version:** 3.0 - Complete Package with All Fixes
**Last Updated:** March 2026
**Status:** Production Ready ✅

Enjoy your voice-first AI assistant! 🎤✨
