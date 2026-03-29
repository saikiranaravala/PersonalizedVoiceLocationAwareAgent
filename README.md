# Personalized Agentic Voice Assistant

A production-ready, voice-first AI assistant with a **React/TypeScript frontend** and a **Python FastAPI + LangChain backend**. It understands natural language, resolves your location from your profile, and orchestrates tool calls for weather, restaurant search, Uber deep links, and local event discovery — all over a real-time WebSocket connection.

---

## Features

- **Voice interaction** — push-to-talk, manual stop, 30-second auto-timeout (Web Speech API)
- **Text chat** — full conversation interface with markdown link rendering
- **Profile-first geolocation** — profile address geocoded via Nominatim; client IP as fallback; server IP never used
- **Restaurant search** — Overpass API (OpenStreetMap), free, no key required
- **Local events** — Ticketmaster Discovery API v2, top 10 upcoming events in 30-day window
- **Uber deep linking** — pre-filled ride links from your profile address
- **Weather** — Open-Meteo API, free, no key required
- **Real-time** — WebSocket for instant bidirectional communication
- **Monitoring** — optional LangSmith agent trace integration

---

## Tech Stack

### Frontend

| Layer | Technology |
| ----- | ---------- |
| Framework | React 18 + TypeScript + Vite |
| Voice input | Web Speech API (Chrome/Edge) |
| Voice output | Speech Synthesis API (browser-native TTS) |
| Transport | WebSocket (`api/client.ts`) |
| Persistence | localStorage (profile, history) |
| Styling | CSS design tokens (`tokens.css`) |

### Backend

| Layer | Technology |
| ----- | ---------- |
| Server | FastAPI + uvicorn |
| Agent | LangChain `create_tool_calling_agent` + `AgentExecutor` |
| LLM | OpenRouter or OpenAI (configurable) |
| Logging | Loguru |
| Tracing | LangSmith (optional) |

### External Services

| Service | Purpose | API Key |
| ------- | ------- | ------- |
| Open-Meteo | Weather | None |
| Overpass API (OSM) | Restaurant search | None |
| Nominatim | Geocoding (1 req/sec) | None |
| ipify.org | Client public IP (browser) | None |
| ipinfo.io | IP → city (backend fallback) | None |
| Ticketmaster Discovery v2 | Local events | `TICKETMASTER_API_KEY` |
| OpenRouter / OpenAI | LLM | `OPENROUTER_API_KEY` |
| LangSmith | Agent tracing | Optional |

---

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenRouter **or** OpenAI API key
- Ticketmaster API key (for events feature)

### Backend Setup

```bash
pip install -r requirements.txt
cp config/.env.example config/.env
# Edit config/.env — add OPENROUTER_API_KEY and TICKETMASTER_API_KEY
python api_server.py
```

### Frontend Setup

```bash
cd ui
npm install
npm run dev
# → http://localhost:5173
```

### Environment Variables

| Variable | Required | Description |
| -------- | -------- | ----------- |
| `OPENROUTER_API_KEY` | Yes | LLM via OpenRouter |
| `OPENAI_API_KEY` | Alt. | LLM directly via OpenAI |
| `TICKETMASTER_API_KEY` | Yes (Events) | Ticketmaster Discovery API v2 |
| `LANGCHAIN_TRACING_V2` | Optional | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | Optional | LangSmith key |
| `LANGCHAIN_PROJECT` | Optional | LangSmith project name |

---

## Project Structure

```
personalized-agentic-assistant/
├── api_server.py                   # FastAPI; WebSocket /ws/{session_id}
├── requirements.txt
├── config/
│   ├── config.yaml                 # Model, location fallback, monitoring
│   ├── .env                        # API keys (gitignored)
│   └── .env.example
├── src/
│   ├── agent/
│   │   └── core.py                 # AgenticAssistant + LocationContextAdapter
│   ├── tools/
│   │   ├── base.py                 # BaseTool — validate → execute → handle_error
│   │   ├── weather.py              # Open-Meteo
│   │   ├── restaurant_finder.py    # Overpass API + Nominatim; 429 retry
│   │   ├── uber.py                 # Uber deep link generator
│   │   ├── events.py               # Ticketmaster Discovery v2; min 10 enforced
│   │   └── save_preferences_tool.py # ws_sender action → frontend localStorage
│   └── services/
│       ├── location.py             # get_current_location(client_ip)
│       └── context.py              # ContextManager; conversation history
├── ui/                             # React/TypeScript frontend
│   ├── src/
│   │   ├── api/client.ts           # WebSocket client; sends client_ip in payload
│   │   ├── hooks/
│   │   │   ├── useVoiceAssistant.ts # Voice + WebSocket + ipify + TTS
│   │   │   └── useUserProfile.ts   # Profile state + localStorage
│   │   ├── components/
│   │   │   ├── core/Button/
│   │   │   ├── ProfileSetup/       # 3-step onboarding modal
│   │   │   ├── ProfileSettings/    # Edit profile + danger zone
│   │   │   └── voice/VoiceButton/  # Push-to-talk with waveform animation
│   │   ├── styles/
│   │   │   ├── tokens.css          # Design token system
│   │   │   └── global.css
│   │   ├── App.tsx                 # linkifyText + 4 quick-action chips
│   │   └── main.tsx
│   ├── _redirects                  # SPA routing (Render/Netlify/Cloudflare)
│   ├── .env                        # VITE_WS_URL, VITE_API_URL
│   └── vite.config.ts
└── docs/
    ├── ARCHITECTURE.md             # Detailed system design and patterns
    ├── DIAGRAMS.md                 # Mermaid diagrams — architecture, flows, journeys
    ├── PRD.md                      # Product requirements document
    ├── PROJECT_SUMMARY.md          # Requirements checklist and engineering decisions
    ├── QUICKSTART.md
    ├── INSTALL_WINDOWS.md
    └── OPENROUTER_GUIDE.md
```

---

## Voice Interaction

| Mode | How to use |
| ---- | ---------- |
| Push-to-talk | Hold the mic button → speak → release |
| Manual stop | Click mic → speak → click **Stop & Send** |
| Auto-timeout | Click mic → speak → auto-sends after **30 seconds** |

Voice works in **Chrome and Edge** (Web Speech API). HTTPS is required in production; HTTP works on localhost.

---

## Location Resolution

The assistant resolves your location through a strict priority chain — the server's IP is never used:

1. Profile `lat`/`lon` coordinates → used directly
2. Profile `address` / `city` / `state` → Nominatim geocode
3. `client_ip` fetched by the browser (ipify.org) → ipinfo.io geolocate
4. Config `fallback_location` → absolute last resort only

---

## API

**WebSocket:** `ws://localhost:8000/ws/{session_id}`

**Client → Server payload:**

```json
{
  "type": "chat",
  "message": "Find Italian restaurants near me",
  "user_profile": { "firstName": "...", "city": "Erie", "state": "PENNSYLVANIA" },
  "client_ip": "24.210.110.237",
  "user_agent": "Mozilla/5.0...",
  "timestamp": 1711234567890
}
```

**Server → Client:**

```json
{ "type": "response", "message": "Here are 5 Italian restaurants...", "success": true }
{ "type": "action",   "action": "save_restaurant", "data": { "name": "...", "address": "..." } }
```

**REST endpoints:**

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/health` | Health check |
| GET | `/context` | Conversation context |
| POST | `/chat` | HTTP fallback |
| POST | `/reset` | Clear conversation history |

---

## Adding a New Tool

1. Create `src/tools/mytool.py`:

```python
from tools.base import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "What it does — the LLM reads this to decide when to call it."

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

1. Optionally add a quick-action chip in `ui/src/App.tsx`.

---

## Configuration

### `config/config.yaml`

```yaml
agent:
  model: "gpt-4"
  temperature: 0.7
  max_iterations: 10
  use_openrouter: true

location:
  use_gps: true
  fallback_location: "New York, NY"

monitoring:
  langsmith_enabled: false
  log_level: "INFO"
```

### `ui/.env`

```bash
VITE_WS_URL=wss://your-backend.onrender.com
VITE_API_URL=https://your-backend.onrender.com
```

---

## Monitoring

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=personalized-agentic-assistant
```

View traces at [smith.langchain.com](https://smith.langchain.com/).

---

## Testing

```bash
# Backend health
python test_backend.py
curl http://localhost:8000/health

# Frontend — standalone test pages (no build required)
ui/test-speech-recognition.html   # Web Speech API mic test
ui/stop-speaking-demo.html        # Speech Synthesis TTS test
ui/websocket-debugger.html        # WebSocket connection debugger
```

---

## Deployment

### Render

| Service | Type | Config |
| ------- | ---- | ------ |
| Backend | Web Service | Start: `python api_server.py` |
| Frontend | Static Site | Build: `cd ui && npm run build`; Publish: `ui/dist` |

Set `VITE_WS_URL=wss://your-backend.onrender.com` in the frontend Static Site env vars. Render's load balancer sets `X-Forwarded-For` automatically so the client IP pipeline works without extra config.

### Nginx (self-hosted)

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

---

## Troubleshooting

| Symptom | Fix |
| ------- | --- |
| Wrong city in results | Check backend logs for `Client IP:` — should be your public IP, not `10.x.x.x`. Ensure profile has `city` and `state` set. |
| Broken links / trailing `)` | Ensure `App.tsx` uses the two-group `LINK_RE` regex in `linkifyText()`. |
| Events returning only 5 results | Check `events.py` has `display_limit = max(10, int(limit))`. |
| Nominatim 429 errors | Built-in retry handles occasional 429s automatically. If persistent, check for extra unguarded Nominatim calls. |
| WebSocket not connecting | Run `curl http://localhost:8000/health`. In production, `VITE_WS_URL` must use `wss://`. |
| Voice not working | Chrome/Edge only. Allow mic permissions. HTTPS required in production. |

---

## Security

- Never commit `config/.env`
- `TICKETMASTER_API_KEY` is backend-only; never in the frontend bundle
- CORS `allow_origins` restricted to known domains in production
- HTTPS required in production (mic access needs a secure context)
- User profile stored in `localStorage` only; never sent to third parties

---

## Documentation

| Document | Purpose |
| -------- | ------- |
| [CLAUDE.md](CLAUDE.md) | Complete codebase and engineering reference |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, patterns, and data flow traces |
| [docs/DIAGRAMS.md](docs/DIAGRAMS.md) | Mermaid diagrams — architecture, sequence, state, ER |
| [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) | Requirements checklist and engineering decisions |
| [docs/PRD.md](docs/PRD.md) | Product requirements document |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | 5-minute setup guide |
| [docs/INSTALL_WINDOWS.md](docs/INSTALL_WINDOWS.md) | Windows-specific installation |
| [docs/OPENROUTER_GUIDE.md](docs/OPENROUTER_GUIDE.md) | OpenRouter integration guide |

---

**Version:** 2.0 — React/TypeScript frontend · WebSocket · Ticketmaster Events · Client IP pipeline · Overpass restaurant search
**Status:** Production Ready ✅
