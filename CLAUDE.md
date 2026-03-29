# 🎤 Personalized Agentic Voice Assistant — Complete Documentation

**A production-ready, voice-first AI assistant with a Python/FastAPI + LangChain backend and a React/TypeScript frontend, featuring agentic tool-calling, WebSocket communication, profile-first geolocation, and a polished chat UI.**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Quick Start](#quick-start)
5. [Voice Control Guide](#voice-control-guide)
6. [Backend Setup](#backend-setup)
7. [Frontend Setup](#frontend-setup)
8. [Tool Integrations](#tool-integrations)
9. [Known Issues & Fixes Applied](#known-issues--fixes-applied)
10. [UX Audit & Recommended Components](#ux-audit--recommended-components)
11. [Troubleshooting](#troubleshooting)
12. [Advanced Configuration](#advanced-configuration)
13. [API Documentation](#api-documentation)
14. [Development Guide](#development-guide)
15. [Deployment](#deployment)
16. [Monitoring & Security](#monitoring--security)

---

## 🎯 Overview

This is a **fully functional, personalized agentic voice assistant** that combines:

- **Voice Recognition** via Web Speech API (push-to-talk, manual stop, 30-second auto-timeout)
- **Natural Language Processing** via OpenRouter/OpenAI through LangChain agents
- **Voice Synthesis** for spoken responses
- **Real-time Communication** through WebSockets (voice and text unified path)
- **Profile-First Geolocation** — profile address geocoded via Nominatim; client IP fallback; server IP never used
- **Location-Aware Tools** — restaurant search, weather, Uber deep linking, local events discovery

### Key Capabilities

- 🎤 **Voice Interaction** — push-to-talk, manual stop, **30-second** auto-timeout
- 💬 **Text Chat** — full conversation interface with markdown link rendering
- 🔧 **Agentic Tool Calling** — LangChain agent selects and calls tools automatically
- 🗺️ **Location Awareness** — profile address geocoded first; client IP (ipify.org) as fallback
- 🍽️ **Restaurant Search** — free via Overpass API (OpenStreetMap)
- 🎟️ **Local Events** — Ticketmaster Discovery API v2, top 10 upcoming events
- 🚗 **Uber Deep Linking** — pre-filled ride links from profile address
- 📊 **Monitoring** — LangSmith integration for agent trace debugging
- 🔄 **Real-time** — WebSocket for instant bidirectional communication

---

## ✨ Features

### Voice Features
- ✅ Push-to-talk — hold to record, release to send
- ✅ Manual stop — click mic, speak, click "Stop & Send"
- ✅ Auto-timeout — **30-second** safety timeout (`VOICE_TIMEOUT_MS = 30_000`)
- ✅ Visual feedback — pulse rings, status dot, state-aware label
- ✅ Speech synthesis — assistant responses spoken aloud
- ✅ Error recovery — automatic retry and WebSocket reconnection

### Backend Features
- ✅ FastAPI — async Python backend
- ✅ LangChain agent — `create_tool_calling_agent` + `AgentExecutor`
- ✅ OpenRouter/OpenAI — flexible LLM provider
- ✅ WebSocket — real-time bidirectional messaging
- ✅ Unified message path — voice and text same handler
- ✅ Client IP extraction — `X-Forwarded-For` / `X-Real-IP` at connection time
- ✅ CORS — configurable for dev and production
- ✅ Health check endpoint

### Frontend Features
- ✅ React + TypeScript + Vite
- ✅ VoiceButton — push-to-talk with waveform and pulse animations
- ✅ ProfileSetup / ProfileSettings — onboarding and preferences
- ✅ Design token system — `tokens.css`
- ✅ `useVoiceAssistant` hook — voice + WebSocket + client IP resolution on mount
- ✅ `useUserProfile` hook — profile state and localStorage persistence
- ✅ Markdown link rendering — `[text](url)` → proper `<a>` tags (no broken `)` in URLs)
- ✅ Quick-action chips — Weather · Restaurants · Ride · Events in single compact row
- ✅ Draggable / resizable chat window
- ✅ SPA routing — `_redirects` for Render/Netlify/Cloudflare

### Tool Integrations
- 🍽️ **Restaurant Search** — Overpass API (OpenStreetMap), free, no key
- 🌤️ **Weather** — Open-Meteo API, free, no key
- 🚗 **Uber** — deep link generation with profile address as pickup
- 🎟️ **Local Events** — Ticketmaster Discovery API v2 (`TICKETMASTER_API_KEY` required)
- 📍 **Geolocation** — profile address → Nominatim geocode → client IP → (never server IP)
- ➕ **Extensible** — add new LangChain tools with minimal boilerplate

---

## 🏗️ Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────┐
│                        Browser                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │            React Frontend (Vite + TypeScript)        │ │
│  │                                                      │ │
│  │  ┌─────────────────┐  ┌──────────────────────────┐  │ │
│  │  │ Voice (Web      │  │  Chat UI + Quick Actions  │ │ │
│  │  │ Speech API)     │  │  Weather·Restaurants      │ │ │
│  │  │ 30s timeout     │  │  Ride·Events chips        │ │ │
│  │  └────────┬────────┘  └────────────┬─────────────┘  │ │
│  │           └──────────┬─────────────┘                 │ │
│  │  ┌───────────────────▼────────────────────────────┐  │ │
│  │  │         useVoiceAssistant hook                  │  │ │
│  │  │  - api/client.ts  WebSocket client              │  │ │
│  │  │  - ipify.org → clientIpRef on mount             │  │ │
│  │  │  - Sends { message, user_profile, client_ip }   │  │ │
│  │  │  - linkifyText: [text](url) → <a> tags          │  │ │
│  │  └────────────────────┬───────────────────────────┘  │ │
│  │  ┌─────────────────────▼──────────────────────────┐  │ │
│  │  │   Speech Synthesis (Text → spoken audio)       │  │ │
│  │  └────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
          │  { message, user_profile, client_ip, user_agent }
          ▼
┌──────────────────────────────────────────────────────────┐
│               Python Backend (FastAPI)                   │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  api_server.py — WebSocket Manager                   │ │
│  │  - Extracts client_ip from X-Forwarded-For          │ │
│  │  - Unified routing (voice + text same path)         │ │
│  └──────────────────────┬──────────────────────────────┘ │
│  ┌───────────────────────▼────────────────────────────┐  │
│  │  agent/core.py — AgenticAssistant                  │  │
│  │  - process_request(msg, user_profile, client_ip)   │  │
│  │  - LocationContextAdapter:                         │  │
│  │    profile lat/lon → geocode address → client IP   │  │
│  └──────────┬─────────────────────────────────────────┘  │
│  ┌──────────▼──────────────────────────────────────────┐ │
│  │  Tools                                              │ │
│  │  restaurant_finder · weather · uber                 │ │
│  │  events (Ticketmaster) · save_preferences           │ │
│  └──────────────────────────────────────────────────── ┘ │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                  External Services                       │
│  OpenRouter/OpenAI · Nominatim · Overpass API (OSM)      │
│  Open-Meteo · ipify.org · ipinfo.io · Ticketmaster API   │
└──────────────────────────────────────────────────────────┘
```

### Location Resolution Priority Chain

```
1. Profile has lat/lng coords     → use directly ✅
2. Profile has address/city/state → Nominatim geocode → use ✅
3. client_ip from browser         → ipinfo.io geolocate → use ✅
4. Server IP (geocoder.ip('me'))  → ❌ never used
```

### Data Flow

**Voice Input:**
```
User speaks → Web Speech API → Transcript
    ↓
useVoiceAssistant.sendMessage(text, profile, userAgent, clientIp)
    ↓
WebSocket → api_server.py (also extracts client_ip from headers)
    ↓
AgenticAssistant.process_request(message, user_profile, client_ip)
    ↓
LangChain Agent → correct location tools → response
    ↓
Response → WebSocket → linkifyText() renders [text](url) as <a> → display + speak
```

---

## 🚀 Quick Start

### Prerequisites

- **Backend:** Python 3.8+, pip
- **Frontend:** Node.js 16+, npm
- **Required API key:** OpenRouter **or** OpenAI
- **Optional API key:** Ticketmaster (for Events tool)
- **Free / no key:** Overpass, Nominatim, Open-Meteo, ipify

### Installation

```bash
# 1. Extract
tar -xzf personalized-agentic-assistant.tar.gz
cd personalized-agentic-assistant

# 2. Backend
pip install -r requirements.txt
cp config/.env.example config/.env
# Edit config/.env — add OPENROUTER_API_KEY and TICKETMASTER_API_KEY

# 3. Frontend
cd ui && npm install
# Edit ui/.env — set VITE_WS_URL for production

# 4. Start backend
python api_server.py
# ✓ Assistant initialized successfully

# 5. Start frontend
cd ui && npm run dev
# ➜ Local: http://localhost:5173/
```

---

## 🎤 Voice Control Guide

### Three Modes

| Mode | How | Best For |
|------|-----|----------|
| Push-to-talk | Hold mic → speak → release | Quick commands |
| Manual stop | Click mic → speak → "Stop & Send" | Longer messages |
| Auto-timeout | Click mic → speak → stops after **30s** | Safety net |

---

## 🛠️ Backend Setup

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ | LLM via OpenRouter |
| `OPENAI_API_KEY` | Alt. | LLM via OpenAI directly |
| `TICKETMASTER_API_KEY` | ✅ for Events | Ticketmaster Discovery API v2 |
| `LANGCHAIN_TRACING_V2` | Optional | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | Optional | LangSmith key |
| `LANGCHAIN_PROJECT` | Optional | LangSmith project name |

### config/config.yaml

```yaml
agent:
  model: "gpt-4"
  temperature: 0.7
  max_iterations: 10
  use_openrouter: true

location:
  use_gps: true
  fallback_location: "New York, NY"   # absolute last resort only

monitoring:
  langsmith_enabled: false
  log_level: "INFO"
```

---

## 💻 Frontend Setup

### Verified File Structure

```
ui/
├── src/
│   ├── api/
│   │   └── client.ts               # WebSocket client; sends client_ip in payload
│   ├── components/
│   │   ├── core/Button/
│   │   │   ├── Button.css
│   │   │   └── Button.tsx
│   │   ├── ProfileSettings/
│   │   │   ├── ProfileSettings.css
│   │   │   └── ProfileSettings.tsx
│   │   ├── ProfileSetup/
│   │   │   ├── ProfileSetup.css
│   │   │   └── ProfileSetup.tsx
│   │   └── voice/VoiceButton/
│   │       ├── VoiceButton.css
│   │       └── VoiceButton.tsx
│   ├── hooks/
│   │   ├── useUserProfile.ts       # Profile state + localStorage
│   │   └── useVoiceAssistant.ts    # Voice + WebSocket + client IP
│   ├── styles/
│   │   ├── global.css
│   │   └── tokens.css              # Design token system
│   ├── types/
│   │   └── userProfile.ts
│   ├── App.css                     # Includes quickactions compact CSS
│   ├── App.tsx                     # linkifyText + 4 quick-action chips
│   └── main.tsx
├── _redirects                      # SPA routing (Render/Netlify/Cloudflare)
├── .env                            # VITE_WS_URL, VITE_API_URL
├── DESIGN_SYSTEM.md
├── INTEGRATION_GUIDE.md
├── index.html
├── package.json
├── README.md
├── SETUP.md
├── stop-speaking-demo.html
├── test-speech-recognition.html
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── websocket-debugger.html
```

### Key Scripts

```bash
npm run dev       # Dev server → localhost:5173
npm run build     # Production build → dist/
npm run preview   # Preview production build
npm run typecheck # TypeScript check
```

---

## 🔧 Tool Integrations

### Restaurant Search (`search_restaurants`)
- **API:** Overpass (OpenStreetMap) — free, no key
- **Geocoding:** Nominatim — free; 1 req/sec; built-in 429 retry with 2s/4s backoff
- **Schema:** `location: Union[str, dict, None]` — normalized internally
- **Result:** top 5 by distance, sorted nearest first

### Weather (`get_weather`)
- **API:** Open-Meteo — free, no key
- **Location:** `LocationContextAdapter` priority chain

### Uber (`book_uber_ride`)
- **Output:** Universal deep link `https://m.uber.com/ul/?...`
- **Pickup:** Profile address geocoded (desktop) or GPS (mobile)

### Local Events (`find_local_events`) — Ticketmaster
- **API:** Ticketmaster Discovery API v2
- **Key:** `TICKETMASTER_API_KEY` in `.env`
- **Window:** today → 30 days, dynamic (never hardcoded)
- **Results:** top 10, sorted soonest first
- **Fields returned:** name, date, venue, address, category, price, url
- **No image fields** — removed to prevent `![Image](url)` rendering in chat
- **Minimum 10 enforced** — `display_limit = max(10, int(limit))` prevents LLM passing `limit=5`
- **Keyword mapping:** "concert" → Music segment ID, "sports" → Sports segment ID, etc.
- **State normalisation:** full state name → 2-letter code (`PENNSYLVANIA` → `PA`)

### Save Tools (`save_restaurant`, `save_uber_trip`)
- Push `{"type": "action", ...}` over WebSocket
- Frontend persists to `localStorage` via `onAction` callback in `App.tsx`

---

## 🐛 Known Issues & Fixes Applied

### 1. Columbus, OH Results Instead of User's City
**Root cause:** `geocoder.ip('me')` on a cloud server resolves the server's IP, not the user's.

**Fix (6 files):**
- `useVoiceAssistant.ts` — fetch client IP via `api.ipify.org` on mount; `clientIpRef`
- `client.ts` — `client_ip` added to `Message` interface and `sendMessage()` payload
- `api_server.py` — extract real IP from `X-Forwarded-For`/`X-Real-IP` at connection time; pass as `client_ip=` to `process_request()`
- `agent/core.py` — `client_ip` param added to `process_request()` and `LocationContextAdapter.get_current_location()`; stored on `location_service._client_ip`
- `services/location.py` — `get_current_location(client_ip=None)` uses `client_ip` over `'me'`
- `tools/restaurant_finder.py` — `_resolve_location()` geocodes profile address before IP; `_profile_address_from_service()` helper

### 2. Nominatim HTTP 429 Rate Limiting
**Root cause:** Profile geocode + restaurant search geocode fired back-to-back with no delay.

**Fix:**
- `restaurant_finder.py` — `_geocode_city()` sleeps `1.1s × attempt`; catches 429; retries 3× with 2s/4s backoff
- `core.py` — `_extract_location_from_profile()` sleeps 1.1s before calling `_geocode_city()`

### 3. Broken Event/Restaurant URLs — Trailing `)` in Links
**Root cause:** `linkifyText()` in `App.tsx` only handled bare URLs via a simple regex. The LLM returns markdown `[label](url)` syntax; the old regex matched the bare URL inside but left `[label](` and `)` as plain text in the DOM.

**Fix:** Replaced `linkifyText` with a two-group regex parser:
```typescript
const LINK_RE = /(\[([^\]]+)\]\((https?:\/\/[^)]+)\))|(https?:\/\/[^\s)]+)/g;
// Group 1-3: full markdown link → <a>{label}</a>
// Group 4:   bare URL           → <a>{url}</a>
```
Processes text in a single left-to-right pass. `[text](url)` renders as a clean clickable link — no brackets, no trailing `)`.

### 4. Events Tool Returning Only 5 Results
**Root cause:** LLM was passing `limit=5` to the tool despite default being 10.

**Fix:** `display_limit = max(10, int(limit))` in `events.py` enforces a floor of 10 regardless of what the LLM passes.

### 5. Image Links in Event Results (`![Image](url)`)
**Root cause:** `image_url` field was included in the events dict; LLM rendered it as markdown image syntax.

**Fix:** Removed entire image-fetching block and `image_url` from `_parse_events()` return dict.

### 6. LangChain Tool Schema Mismatch
**Root cause:** `location` param typed as `dict`; LLM passed a string → Pydantic error.

**Fix:** `Union[str, dict, None]` with internal normalization.

### 7. `get_location()` Key Name Mismatch
**Root cause:** Code referenced `lat`/`lon`; service returns `latitude`/`longitude`.

**Fix:** All references updated to `latitude`/`longitude`.

### 8. Pointer Capture Swallowing Clicks (Drag)
**Fix:** Drag isolated to child `div`; `stopPropagation` on control buttons.

### 9. Resize Handle Losing Events
**Fix:** `pointermove`/`pointerup` on `document`; `overflow: visible` on container.

### 10. Voice Timeout Too Short
**Change:** Hardcoded `10000` → named constant `VOICE_TIMEOUT_MS = 30_000`.

### 11. Events Chip Wrapping to Second Row
**Root cause:** 4 chips too wide for default 380px window with default padding/font-size.

**Fix:** Added `.chat-window__quickactions--compact` modifier class:
```css
.chat-window__quickactions { flex-wrap: nowrap; overflow-x: auto; }
.chat-window__quickactions--compact .chat-window__qa-btn {
  padding: 5px 9px; font-size: 12px; flex-shrink: 0;
}
```

---

## 🎨 UX Audit & Recommended Components

Identified issues — components designed but not yet integrated into codebase.

| Issue | Recommended Fix |
|-------|----------------|
| CTA overload | FAB (Floating Action Button) |
| Mixed icon libraries | Unify to Lucide React |
| No async feedback | Toast notification system |
| Mobile thumb-zone | SlideUpInput anchored to bottom |
| No help path | SupportButton component |

### Target Structure (when integrating):
```
ui/src/components/
├── core/Button/          ← exists ✅
├── FAB/                  ← planned
├── Toast/                ← planned
├── SlideUpInput/         ← planned
├── SupportButton/        ← planned
├── ProfileSettings/      ← exists ✅
├── ProfileSetup/         ← exists ✅
└── voice/VoiceButton/    ← exists ✅
```

---

## 🔍 Troubleshooting

### Wrong City in Results
1. Backend logs: `Client IP:` should show real public IP (not `10.x.x.x`)
2. Backend logs: `Geocoded user profile location` should show your city's coordinates
3. Check profile has `city` and `state` set in ProfileSettings
4. If 429 error on geocode — built-in retry handles it; wait 10s and retry

### Broken Links / Trailing `)` in Chat
- Ensure `App.tsx` has the updated `linkifyText` using `LINK_RE` regex (not the old `urlRegex`)
- The fix is frontend-only — backend sends clean markdown

### Events Tool Issues
- `TICKETMASTER_API_KEY` must be set in `config/.env`
- If only 5 results: ensure `events.py` has `display_limit = max(10, int(limit))`
- If image links appear in chat: ensure `image_url` field is removed from `_parse_events()`

### Nominatim 429 Errors
- Built-in retry handles occasional 429s automatically
- If persistent: check for other unguarded Nominatim calls elsewhere in code

### WebSocket Not Connecting
- `curl http://localhost:8000/health` — confirm backend running
- `VITE_WS_URL` must use `wss://` on HTTPS deployments (Render)
- CORS `allow_origins` must include your frontend URL

### Voice Not Working
- Chrome/Edge only (Web Speech API)
- Allow mic permissions
- HTTPS required in production; HTTP works on localhost
- Test with `ui/test-speech-recognition.html`

---

## ⚙️ Advanced Configuration

### Voice Timeout
```typescript
// ui/src/hooks/useVoiceAssistant.ts
const VOICE_TIMEOUT_MS = 30_000; // 30 seconds
```

### WebSocket URL (Production)
```bash
# ui/.env
VITE_WS_URL=wss://your-backend.onrender.com
VITE_API_URL=https://your-backend.onrender.com
```

### Events Tool — Date Window
```python
# tools/events.py — computed dynamically, never hardcoded
now = datetime.now(timezone.utc)
end = now + timedelta(days=30)
```

### Nominatim Rate Limit Tuning
```python
# tools/restaurant_finder.py
time.sleep(1.1 * (attempt + 1))  # increase if still hitting 429
max_retries = 3
```

---

## 📡 API Documentation

### WebSocket Endpoint
```
ws://localhost:8000/ws/{session_id}
wss://your-backend.onrender.com/ws/{session_id}
```

**Client → Server:**
```json
{
  "type": "chat",
  "message": "What events are happening near me?",
  "user_profile": {
    "firstName": "SAI KIRAN",
    "address": "5013 Burgundy Dr",
    "city": "Erie",
    "state": "PENNSYLVANIA",
    "country": "United States"
  },
  "user_agent": "Mozilla/5.0...",
  "client_ip": "24.210.110.237",
  "timestamp": 1711234567890
}
```

**Server → Client (response):**
```json
{ "type": "response", "message": "Here are upcoming events in Erie...", "success": true }
```

**Server → Client (action — localStorage persistence):**
```json
{ "type": "action", "action": "save_restaurant", "data": { "name": "...", "address": "..." } }
```

### REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/context` | Conversation context |
| POST | `/chat` | HTTP fallback |
| POST | `/reset` | Clear history |

---

## 👩‍💻 Development Guide

### Adding a New Tool

1. Create `src/tools/mytool.py`:
```python
from tools.base import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "What it does — LLM reads this to decide when to call it."

    def execute(self, param: str, **kwargs) -> dict:
        return {"success": True, "result": f"Did {param}"}
```

2. Register in `src/agent/core.py` `_initialize_tools()`:
```python
from tools.mytool import MyTool
my_tool = MyTool(self.location_adapter)
tools.append(StructuredTool.from_function(
    func=my_tool.execute, name=my_tool.name, description=my_tool.description,
))
```

3. Add quick-action chip in `App.tsx` if needed:
```tsx
// In handleQuickAction messages map:
mytool: "Trigger phrase for my tool",

// In quick actions bar:
<button className="chat-window__qa-btn" onClick={() => handleQuickAction('mytool')} disabled={!isConnected}>
  <MyToolIcon /> <span>MyTool</span>
</button>
```

### Key Engineering Principles

- **Profile-first location** — geocode profile address before any IP lookup; server IP is never acceptable
- **Client IP pipeline** — `ipify.org` (browser) → WS payload → HTTP headers → `process_request()` → `location_service`
- **Nominatim rate limiting** — sleep ≥1.1s before every call; catch 429 and retry with backoff
- **Flexible tool schemas** — `Union[str, dict, None]` for location params; normalize internally
- **Markdown link rendering** — always use the two-group `LINK_RE` regex; never plain URL-only regex
- **Events minimum 10** — `max(10, int(limit))` floor; LLM often passes smaller values
- **No image fields in tool output** — LLM will render them as `![Image](url)` in chat
- **Unified backend path** — voice and text through same WebSocket handler
- **Drag isolation** — pointer capture on drag handle child only
- **Resize on document** — `pointermove`/`pointerup` on `document`, not the handle element

---

## 🚀 Deployment

### Render (Current Platform)

**Backend (Web Service):**
- Build: `pip install -r requirements.txt`
- Start: `python api_server.py`
- Env vars: `OPENROUTER_API_KEY`, `TICKETMASTER_API_KEY`
- Render's load balancer sets `X-Forwarded-For` automatically ✅

**Frontend (Static Site):**
- Build: `cd ui && npm run build`
- Publish: `ui/dist`
- Env vars: `VITE_WS_URL=wss://your-backend.onrender.com`
- `_redirects` handles SPA routing ✅

### Nginx (Self-hosted)
```nginx
location / {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### systemd
```ini
[Service]
WorkingDirectory=/path/to/project
EnvironmentFile=/path/to/config/.env
ExecStart=/usr/bin/python3 -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
```

### Docker Compose
```yaml
services:
  backend:
    build: { context: ., dockerfile: Dockerfile.backend }
    ports: ["8000:8000"]
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - TICKETMASTER_API_KEY=${TICKETMASTER_API_KEY}
    restart: unless-stopped
  frontend:
    build: { context: ., dockerfile: Dockerfile.frontend }
    ports: ["80:80"]
    depends_on: [backend]
    restart: unless-stopped
```

---

## 📊 Monitoring & Security

### LangSmith
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=personalized-agentic-assistant
```
View at: https://smith.langchain.com/

### Security Checklist
- Never commit `config/.env`
- Restrict CORS `allow_origins` to production domain
- HTTPS required in production (mic access needs secure context)
- Add `slowapi` rate limiting for public deployments
- Rotate API keys regularly
- `TICKETMASTER_API_KEY` — backend only, never in frontend bundle

---

## 📖 Reference

### Standalone Test Pages
```
ui/test-speech-recognition.html  — Web Speech API mic test
ui/stop-speaking-demo.html       — Speech synthesis test
ui/websocket-debugger.html       — WebSocket connection debugger
```

### External Docs
- LangChain: https://python.langchain.com/docs/
- FastAPI: https://fastapi.tiangolo.com/
- Ticketmaster API: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
- Overpass API: https://overpass-api.de/
- Nominatim: https://nominatim.org/release-docs/latest/api/Search/
- Open-Meteo: https://open-meteo.com/
- Web Speech API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

### Quick Commands
```bash
# Start (dev)
python api_server.py &
cd ui && npm run dev

# Health check
curl http://localhost:8000/health

# Debug
open ui/websocket-debugger.html
open ui/test-speech-recognition.html
```

---

**Version:** 6.0 — Events tool (Ticketmaster); markdown link fix; 4-chip compact row; top-10 enforcement; image field removed
**Last Updated:** March 2026
**Status:** Production Ready ✅
