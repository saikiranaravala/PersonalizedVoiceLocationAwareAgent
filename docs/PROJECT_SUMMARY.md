# Project Summary: Personalized Agentic Voice Assistant — v2.0

## Overview

A production-grade, voice-first AI assistant with a **React/TypeScript + Vite frontend** and a **Python FastAPI + LangChain backend**, featuring agentic tool-calling, WebSocket real-time communication, profile-first geolocation, and a polished chat UI. The system runs in any modern browser and deploys to Render (or any cloud/self-hosted platform).

---

## Requirements Implementation

### Core Architectural Pillars

| Pillar | Status | Implementation |
| ------ | ------ | -------------- |
| Location Awareness | ✅ | Profile address → Nominatim geocode → client IP → ipinfo.io; server IP never used |
| Extensible Tool-Use | ✅ | 6 tools: Weather, RestaurantFinder, Uber, Events, SaveRestaurant, SaveUberTrip |
| Deep Linking | ✅ | `https://m.uber.com/ul/` universal deep link with geocoded pickup coords |
| Production Monitoring | ✅ | LangSmith tracing; Loguru structured logging |
| Voice Interface | ✅ | Web Speech API — push-to-talk, manual stop, 30s auto-timeout |
| Real-time Communication | ✅ | WebSocket — unified voice + text path |
| Local Events Discovery | ✅ | Ticketmaster Discovery API v2 — top 10, 30-day window |

### Tech Stack

#### Frontend

| Technology | Role |
| ---------- | ---- |
| React 18 + TypeScript | UI framework |
| Vite | Build tool & dev server |
| Web Speech API | Voice recognition (browser-native, Chrome/Edge) |
| Speech Synthesis API | TTS — spoken responses (browser-native) |
| WebSocket (native) | Real-time bidirectional communication |
| localStorage | Profile & history persistence |
| CSS design tokens | `tokens.css` — consistent theming |

#### Backend

| Technology | Role |
| ---------- | ---- |
| Python 3.8+ | Runtime |
| FastAPI + uvicorn | Async web server + WebSocket endpoint |
| LangChain | `create_tool_calling_agent` + `AgentExecutor` |
| OpenRouter / OpenAI | LLM provider (configurable) |
| Loguru | Structured logging |
| LangSmith | Optional agent trace observability |

#### External Services (all free unless noted)

| Service | Purpose | Key Required |
| ------- | ------- | ------------ |
| Open-Meteo | Weather data | No |
| Overpass API (OSM) | Restaurant search | No |
| Nominatim | Geocoding (1 req/sec) | No |
| ipify.org | Client public IP (browser) | No |
| ipinfo.io | IP → city (backend fallback) | No |
| Ticketmaster Discovery v2 | Local events | Yes — `TICKETMASTER_API_KEY` |
| OpenRouter / OpenAI | LLM | Yes — `OPENROUTER_API_KEY` |
| LangSmith | Agent tracing | Optional |

---

## Agentic Loop

```
1. Ingestion     Voice (Web Speech API) or text input from chat
2. Enrichment    Client IP resolved (ipify.org on mount); profile loaded from localStorage
3. Transport     WebSocket payload: { message, user_profile, client_ip, user_agent }
4. Location      Profile address → Nominatim geocode → client IP fallback (server IP never used)
5. Reasoning     LangChain LLM selects tool, constructs params, location hint injected
6. Execution     Tool calls Overpass / Open-Meteo / Ticketmaster / Uber deep link
7. Response      JSON → WebSocket → linkifyText() → chat bubble + TTS
8. Persistence   Action messages (save_restaurant / save_uber_trip) → localStorage
```

### Example Flow

```
User: "Find Italian restaurants near me and book an Uber to the first one"
   ↓
search_restaurants(query="Italian")
  → profile city="Erie, PA" → Nominatim → (42.13, -80.09)
  → Overpass API → 5 Italian restaurants sorted by distance
   ↓
book_uber_ride(destination="Aldo's Restaurant, 108 E 10th St, Erie PA")
  → pickup = profile address → Nominatim → (42.068, -80.123)
  → https://m.uber.com/ul/?action=setPickup&pickup[lat]=42.068&...
   ↓
SaveRestaurantTool → ws_sender → { type: "action" } → localStorage
```

---

## Project Structure

```
personalized-agentic-assistant/
├── api_server.py                   # FastAPI server; WebSocket /ws/{session_id}
├── requirements.txt
├── config/
│   ├── config.yaml                 # Agent model, location fallback, monitoring
│   ├── .env                        # API keys (gitignored)
│   └── .env.example
├── src/
│   ├── agent/
│   │   └── core.py                 # AgenticAssistant + LocationContextAdapter
│   ├── tools/
│   │   ├── base.py                 # BaseTool — validate → execute → handle_error
│   │   ├── weather.py              # Open-Meteo
│   │   ├── restaurant_finder.py    # Overpass API + Nominatim; 429 retry
│   │   ├── uber.py                 # Deep link generator
│   │   ├── events.py               # Ticketmaster Discovery v2; min 10 enforced
│   │   └── save_preferences_tool.py # ws_sender action push → localStorage
│   └── services/
│       ├── location.py             # get_current_location(client_ip)
│       └── context.py              # ContextManager; conversation history
├── ui/                             # React/TypeScript frontend
│   ├── src/
│   │   ├── api/client.ts           # WebSocket client; client_ip in payload
│   │   ├── hooks/
│   │   │   ├── useVoiceAssistant.ts # Voice + WS + ipify + TTS
│   │   │   └── useUserProfile.ts   # Profile state + localStorage
│   │   ├── components/
│   │   │   ├── core/Button/
│   │   │   ├── ProfileSetup/       # 3-step onboarding modal
│   │   │   ├── ProfileSettings/    # Edit profile + danger zone
│   │   │   └── voice/VoiceButton/  # Push-to-talk with waveform
│   │   ├── styles/
│   │   │   ├── tokens.css          # Design token system
│   │   │   └── global.css
│   │   ├── types/userProfile.ts
│   │   ├── App.tsx                 # linkifyText + 4 quick-action chips
│   │   └── main.tsx
│   ├── _redirects                  # SPA routing (Render/Netlify/Cloudflare)
│   ├── .env                        # VITE_WS_URL, VITE_API_URL
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
└── docs/
    ├── ARCHITECTURE.md
    ├── DIAGRAMS.md
    ├── PRD.md
    ├── PROJECT_SUMMARY.md          # this file
    ├── QUICKSTART.md
    ├── INSTALL_WINDOWS.md
    └── ...
```

---

## Key Engineering Decisions

### 1. Profile-First Geolocation

Server IP geolocation (`geocoder.ip('me')`) always resolves the cloud host city, not the user's city. The fix is a strict priority chain:

1. Profile `lat`/`lon` → use directly
2. Profile `address`/`city`/`state` → Nominatim geocode
3. `client_ip` (browser fetches via ipify.org) → ipinfo.io
4. Server IP → **never reached in normal operation**

### 2. Nominatim Rate Limiting

Nominatim enforces 1 req/sec. Two-level sleep strategy prevents 429 errors:

- **Level 1 (core.py):** `sleep(1.1s)` before profile geocode
- **Level 2 (restaurant_finder.py):** `sleep(1.1s × attempt)` before each retry; `sleep(2^attempt)` backoff on 429

### 3. Markdown Link Rendering

The LLM returns `[label](url)` syntax. A two-group regex processes text in a single left-to-right pass:

```typescript
const LINK_RE = /(\[([^\]]+)\]\((https?:\/\/[^)]+)\))|(https?:\/\/[^\s)]+)/g;
// Group 1-3: [label](url) → <a>label</a>   — no brackets, no trailing )
// Group 4:   bare URL     → <a>url</a>
```

### 4. Events Tool — Safety Floors

- `display_limit = max(10, int(limit))` — LLM cannot return fewer than 10 results
- No `image_url` field in `_parse_events()` — prevents `![Image](url)` rendering in chat
- Date window computed dynamically: `now → now + timedelta(days=30)`

### 5. WebSocket Action Pattern

Save tools push `{ type: "action", action: "save_restaurant", data: {...} }` via an injected `ws_sender` callable rather than returning data in the tool result. Frontend `onAction` handler persists to localStorage. This keeps backend tools decoupled from frontend storage.

---

## Quick Start

```bash
# Backend
pip install -r requirements.txt
cp config/.env.example config/.env
# Add OPENROUTER_API_KEY and TICKETMASTER_API_KEY to config/.env
python api_server.py

# Frontend (new terminal)
cd ui && npm install && npm run dev
# → http://localhost:5173
```

### Environment Variables

| Variable | Required | Purpose |
| -------- | -------- | ------- |
| `OPENROUTER_API_KEY` | Yes | LLM via OpenRouter |
| `OPENAI_API_KEY` | Alt. | LLM directly via OpenAI |
| `TICKETMASTER_API_KEY` | Yes (Events) | Ticketmaster Discovery API v2 |
| `LANGCHAIN_TRACING_V2` | Optional | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | Optional | LangSmith key |

---

## Voice Interaction Modes

| Mode | How | Timeout |
| ---- | --- | ------- |
| Push-to-talk | Hold mic button → release to send | N/A |
| Manual stop | Click mic → speak → click Stop & Send | N/A |
| Auto-timeout | Click mic → speak → auto-sends | 30s (`VOICE_TIMEOUT_MS`) |

---

## API Reference

**WebSocket:** `ws://localhost:8000/ws/{session_id}`

**Client → Server:**

```json
{
  "type": "chat",
  "message": "Find events near me",
  "user_profile": { "firstName": "...", "city": "Erie", "state": "PENNSYLVANIA" },
  "client_ip": "24.210.110.237",
  "user_agent": "Mozilla/5.0...",
  "timestamp": 1711234567890
}
```

**Server → Client:**

```json
{ "type": "response", "message": "Here are 10 events...", "success": true }
{ "type": "action",   "action": "save_restaurant", "data": { "name": "...", "address": "..." } }
```

**REST:**

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/health` | Health check |
| GET | `/context` | Conversation context |
| POST | `/chat` | HTTP fallback |
| POST | `/reset` | Clear conversation |

---

## Testing

```bash
# Backend
python test_backend.py
curl http://localhost:8000/health

# Frontend standalone test pages (no build required)
ui/test-speech-recognition.html  — Web Speech API mic test
ui/stop-speaking-demo.html        — Speech Synthesis TTS test
ui/websocket-debugger.html        — WebSocket connection debugger
```

### Critical Test Cases

| Test | Pass Criteria |
| ---- | ------------- |
| Location pipeline | Logs show Erie, PA coords — not server host city |
| Events minimum | Response always contains ≥ 10 events |
| Link rendering | No `[`, `]`, `(`, `)` visible in chat bubbles |
| Nominatim 429 | User sees results; logs show retry |
| Voice timeout | Recording active at 25s; stops at 30s |
| Reconnect | App reconnects automatically after backend restart |

---

## Deployment

### Render (current)

| Service | Type | Config |
| ------- | ---- | ------ |
| Backend | Web Service | `python api_server.py`; env vars set in dashboard |
| Frontend | Static Site | `cd ui && npm run build`; publish `ui/dist`; `VITE_WS_URL=wss://...` |

Render's load balancer sets `X-Forwarded-For` automatically — client IP pipeline works without extra config.

### Self-Hosted (Nginx + systemd)

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

---

## Known Issues & Fixes Applied

| Issue | Fix |
| ----- | --- |
| Wrong city results (server IP used) | Client IP pipeline: ipify.org → WS payload → `process_request` |
| Nominatim HTTP 429 | Pre-sleep + exponential backoff in `restaurant_finder.py` and `core.py` |
| Trailing `)` in chat links | Two-group `LINK_RE` regex in `App.tsx` `linkifyText()` |
| Events returning only 5 results | `display_limit = max(10, int(limit))` floor in `events.py` |
| Image links in event results | Removed `image_url` field from `_parse_events()` |
| LangChain tool schema mismatch | `location: Union[str, dict, None]` with internal normalisation |
| Voice timeout too short | `VOICE_TIMEOUT_MS = 30_000` named constant (was hardcoded 10s) |
| Quick-action chips wrapping | `flex-wrap: nowrap` + `--compact` modifier class |

---

## Future Enhancements

### Near-Term (v2.1)

- Toast notification system (replace `alert()`)
- FAB replacing competing CTAs
- SlideUpInput for mobile thumb zone
- Lucide React icon unification
- ARIA/accessibility improvements

### Medium-Term (v3.0)

- PostgreSQL for preference persistence
- Redis caching (Nominatim, Overpass, Ticketmaster)
- Native iOS/Android app
- Calendar tool integration
- Progressive Web App (PWA)

### Long-Term

- Microservices decomposition
- Kubernetes deployment
- Plugin marketplace
- Edge/offline capability

---

## Success Criteria

| Criteria | Status |
| -------- | ------ |
| Voice interaction in browser | ✅ Web Speech API (Chrome/Edge) |
| Profile-first location accuracy | ✅ Nominatim geocode before any IP lookup |
| Real-time WebSocket communication | ✅ Unified voice + text path |
| Restaurant search (free, no key) | ✅ Overpass API + Nominatim |
| Local events discovery | ✅ Ticketmaster Discovery v2 |
| Uber deep linking | ✅ Universal link with geocoded pickup |
| Markdown link rendering | ✅ Two-group regex; no trailing `)` |
| Production monitoring | ✅ LangSmith + Loguru |
| Render deployment | ✅ Backend Web Service + Frontend Static Site |
| Comprehensive documentation | ✅ ARCHITECTURE.md, DIAGRAMS.md, PRD.md, CLAUDE.md |

---

## Documentation Index

| Document | Purpose |
| -------- | ------- |
| [CLAUDE.md](../CLAUDE.md) | Complete codebase and engineering reference |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Detailed system design and patterns |
| [DIAGRAMS.md](DIAGRAMS.md) | Mermaid diagrams — architecture, flows, journeys |
| [PRD.md](PRD.md) | Product requirements document |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide |
| [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) | Windows-specific installation |
| [OPENROUTER_GUIDE.md](OPENROUTER_GUIDE.md) | OpenRouter integration guide |

---

**Version:** 2.0 — React/TypeScript frontend; WebSocket; Ticketmaster Events; client IP pipeline; Overpass restaurant search
**Last Updated:** March 2026
**Status:** Production Ready ✅
