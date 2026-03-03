# Complete Setup Guide - Backend + Frontend

## 🚀 Quick Start (3 Steps)

### Step 1: Install Backend Dependencies

```bash
# Navigate to project root
cd personalized-agentic-assistant

# Install Python dependencies
pip install -r requirements.txt --break-system-packages
```

**Windows shortcut:**
```bash
setup.bat
```

### Step 2: Configure API Keys

```bash
# Copy environment template
copy config\.env.example config\.env

# Edit with your API key
notepad config\.env
```

Add either:
```env
# Option 1: OpenAI (direct)
OPENAI_API_KEY=sk-your-key-here

# Option 2: OpenRouter (recommended)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**And set in config.yaml:**
```yaml
agent:
  use_openrouter: true  # or false for OpenAI
  model: "anthropic/claude-3-sonnet"
```

### Step 3: Start Both Servers

**Terminal 1 - Backend:**
```bash
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd ui
npm install
npm run dev
```

**Access the app:** `http://localhost:5173`

---

## 📋 Detailed Installation

### Prerequisites

- ✅ Python 3.11.9
- ✅ Node.js 18+ (for frontend)
- ✅ OpenAI or OpenRouter API key

### Backend Setup

1. **Install Python packages:**
```bash
pip install -r requirements.txt --break-system-packages
```

Key packages installed:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `websockets` - Real-time communication
- `langchain` - AI orchestration
- All existing assistant dependencies

2. **Verify installation:**
```bash
python -c "from fastapi import FastAPI; print('FastAPI OK')"
python -c "from agent.core import AgenticAssistant; print('Assistant OK')"
```

3. **Configure environment:**
```bash
# Create config/.env
OPENAI_API_KEY=sk-...
# or
OPENROUTER_API_KEY=sk-or-v1-...
```

4. **Start the backend:**
```bash
python api_server.py
```

You should see:
```
🚀 Personalized Agentic Assistant API Server
✓ Assistant initialized successfully
Server running on http://localhost:8000
```

### Frontend Setup

1. **Navigate to UI folder:**
```bash
cd ui
```

2. **Install Node packages:**
```bash
npm install
```

If you see peer dependency warnings:
```bash
npm install --legacy-peer-deps
```

3. **Start development server:**
```bash
npm run dev
```

You should see:
```
VITE v5.0.0  ready in 500 ms
➜  Local:   http://localhost:5173/
```

4. **Open browser:**
```
http://localhost:5173
```

---

## 🧪 Testing the Setup

### Test Backend API

**Terminal:**
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "agentic-assistant",
  "assistant_initialized": true
}
```

**Test chat endpoint:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Hello\"}"
```

### Test Frontend

Open `http://localhost:5173` and you should see:
- ✅ Voice button in center
- ✅ Theme switcher (top-right)
- ✅ Empty state message
- ✅ Quick action buttons (bottom)

Click the voice button - you should see animations!

---

## 🔗 API Endpoints

### REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/chat` | POST | Send message |
| `/context` | GET | Get conversation context |
| `/reset` | POST | Reset conversation |

### WebSocket

```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws/user123');

// Send message
ws.send(JSON.stringify({
  type: 'chat',
  message: 'What is the weather?'
}));

// Receive response
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Response:', data);
};
```

---

## 🛠️ Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'fastapi'"**
```bash
pip install fastapi uvicorn --break-system-packages
```

**"Assistant not initialized"**
- Check `config/.env` has valid API key
- Verify key format: `sk-...` (OpenAI) or `sk-or-v1-...` (OpenRouter)
- Check console logs for error messages

**"Port 8000 already in use"**
```bash
# Windows - find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in api_server.py:
uvicorn.run(app, port=8001)
```

### Frontend Issues

**"npm install" fails**
```bash
npm install --legacy-peer-deps
```

**"Port 5173 already in use"**
```bash
# Kill the process
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Or edit vite.config.ts to use different port
```

**"Cannot connect to backend"**
- Make sure backend is running on port 8000
- Check CORS settings in `api_server.py`
- Verify API URL in frontend (should be `http://localhost:8000`)

### CORS Errors

If you see CORS errors in browser console, make sure backend is running and includes your frontend URL:

```python
# In api_server.py
allow_origins=[
    "http://localhost:5173",  # Your frontend URL
]
```

---

## 📁 Project Structure

```
personalized-agentic-assistant/
├── api_server.py              # 👈 FastAPI backend server
├── setup.bat                  # Windows setup script
├── start_backend.bat          # Start backend server
├── requirements.txt           # Python dependencies (updated)
├── src/
│   ├── agent/                 # AI agent code
│   ├── tools/                 # Tools (weather, uber, etc.)
│   └── services/              # Location, speech, context
├── config/
│   ├── config.yaml            # Configuration
│   └── .env                   # API keys (create this!)
└── ui/
    ├── src/
    │   ├── App.tsx            # Main React app
    │   ├── components/        # UI components
    │   └── styles/            # Design system
    ├── package.json           # Node dependencies
    └── vite.config.ts         # Vite config
```

---

## 🚀 Development Workflow

### Daily Development

1. **Start Backend** (Terminal 1):
```bash
python api_server.py
```

2. **Start Frontend** (Terminal 2):
```bash
cd ui && npm run dev
```

3. **Open Browser**:
```
http://localhost:5173
```

4. **Make changes**:
- Backend changes: Server auto-reloads
- Frontend changes: Hot module reload (instant)

### Testing Changes

**Backend:**
```bash
# Test API directly
curl http://localhost:8000/health

# Or use Python
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

**Frontend:**
```bash
# Type checking
npm run type-check

# Linting
npm run lint
```

---

## 🎯 Next Steps

### 1. Customize Theme
Edit `ui/src/styles/tokens.css`:
```css
:root {
  --color-primary-500: #your-brand-color;
}
```

### 2. Add New Tools
See `ARCHITECTURE.md` for adding new capabilities.

### 3. Deploy to Production

**Build Frontend:**
```bash
cd ui
npm run build
```

**Start Production Server:**
```bash
python api_server.py
```

Access at: `http://localhost:8000`

---

## 📚 Documentation

- **README.md** - Project overview
- **ui/README.md** - Frontend documentation
- **ui/DESIGN_SYSTEM.md** - Design specifications
- **ui/INTEGRATION_GUIDE.md** - Backend integration details
- **TROUBLESHOOTING.md** - Common issues
- **QUICKFIX.md** - OpenRouter error fixes

---

## ✅ Installation Checklist

- [ ] Python 3.11.9 installed
- [ ] Node.js 18+ installed
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`cd ui && npm install`)
- [ ] API key configured in `config/.env`
- [ ] Backend running (`python api_server.py`)
- [ ] Frontend running (`cd ui && npm run dev`)
- [ ] Browser open at `http://localhost:5173`
- [ ] Voice button working with animations

---

**You're all set!** 🎉

The complete full-stack voice assistant is now running with:
- ✅ Python backend with FastAPI
- ✅ React frontend with voice UI
- ✅ WebSocket real-time communication
- ✅ RESTful API endpoints
- ✅ Complete design system
- ✅ Production-ready code

**Need help?** Check the troubleshooting section above or the detailed documentation files.
