# Architecture Documentation
## Personalized Agentic Voice Assistant — v2.0

---

## System Overview

The assistant is built on a modular, production-ready architecture with a clear separation between the React/TypeScript frontend, the FastAPI/LangChain backend, and a set of free and paid external services. The central design principle is **profile-first geolocation** — user location is always resolved from the saved profile address, never from the cloud server's IP.

```
┌──────────────────────────────────────────────────────────────┐
│                        Browser                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          React Frontend  (Vite + TypeScript)          │   │
│  │                                                        │   │
│  │  ┌──────────────────┐   ┌────────────────────────┐   │   │
│  │  │  Voice (Web      │   │  Chat UI               │   │   │
│  │  │  Speech API)     │   │  ProfileSetup/Settings  │   │   │
│  │  │  30s timeout     │   │  Quick chips (4)        │   │   │
│  │  │  push-to-talk    │   │  Weather·Food·Ride      │   │   │
│  │  │  manual stop     │   │  ·Events                │   │   │
│  │  └────────┬─────────┘   └───────────┬────────────┘   │   │
│  │           └──────────────┬──────────┘                 │   │
│  │  ┌───────────────────────▼──────────────────────────┐ │   │
│  │  │          useVoiceAssistant hook                   │ │   │
│  │  │  api/client.ts  WebSocket client                  │ │   │
│  │  │  ipify.org → clientIpRef  (on mount)              │ │   │
│  │  │  Sends { message, user_profile, client_ip }       │ │   │
│  │  │  linkifyText: [label](url) → <a> tags             │ │   │
│  │  │  Auto-reconnect  (5× exponential backoff)         │ │   │
│  │  └───────────────────────┬──────────────────────────┘ │   │
│  │  ┌───────────────────────▼──────────────────────────┐ │   │
│  │  │   Speech Synthesis  (Text → spoken audio)        │ │   │
│  │  └──────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
            │
            │  WebSocket  wss://backend/ws/{session_id}
            │  Payload: { type, message, user_profile,
            │             client_ip, user_agent, timestamp }
            ▼
┌──────────────────────────────────────────────────────────────┐
│               Python Backend  (FastAPI + uvicorn)            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  api_server.py — WebSocket Manager                    │   │
│  │  • Extracts client_ip from X-Forwarded-For header     │   │
│  │  • Unified routing  (voice + text same handler)       │   │
│  │  • Injects ws_sender per request  (action pushback)   │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                          │                                    │
│  ┌───────────────────────▼───────────────────────────────┐  │
│  │  agent/core.py — AgenticAssistant                     │  │
│  │                                                        │  │
│  │  process_request(msg, user_profile, client_ip)         │  │
│  │                                                        │  │
│  │  ┌────────────────────────────────────────────────┐   │  │
│  │  │  LocationContextAdapter                        │   │  │
│  │  │  Priority:                                     │   │  │
│  │  │  1. profile lat/lon  → use directly            │   │  │
│  │  │  2. profile address  → Nominatim geocode       │   │  │
│  │  │  3. client_ip        → ipinfo.io geolocate     │   │  │
│  │  │  4. server IP        → NEVER used              │   │  │
│  │  └────────────────────────────────────────────────┘   │  │
│  │                                                        │  │
│  │  LangChain  create_tool_calling_agent + AgentExecutor  │  │
│  │  Location hint injected into every prompt              │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  Tool Layer                                            │  │
│  │                                                        │  │
│  │  ┌─────────────┐ ┌───────────┐ ┌───────────────────┐ │  │
│  │  │ restaurant  │ │  weather  │ │  events           │ │  │
│  │  │ _finder.py  │ │  .py      │ │  .py              │ │  │
│  │  │ Overpass API│ │ Open-Meteo│ │ Ticketmaster v2   │ │  │
│  │  │ Nominatim   │ │ free/nokey│ │ top 10, 30 days   │ │  │
│  │  │ 429 retry   │ │           │ │ min 10 enforced   │ │  │
│  │  └─────────────┘ └───────────┘ └───────────────────┘ │  │
│  │  ┌─────────────┐ ┌──────────────────────────────────┐ │  │
│  │  │  uber.py    │ │  save_preferences_tool.py        │ │  │
│  │  │ deep link   │ │  → ws_sender → action msg        │ │  │
│  │  │ profile addr│ │  → frontend localStorage         │ │  │
│  │  └─────────────┘ └──────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Service Layer                                          │ │
│  │  services/location.py  get_current_location(client_ip) │ │
│  │  services/context.py   ContextManager                  │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────────┐
│                    External Services                         │
│                                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ OpenRouter   │ │  Nominatim   │ │  Overpass API (OSM)  │ │
│  │ / OpenAI     │ │  (geocoding) │ │  (restaurant search) │ │
│  │  LLM         │ │  free, 1/sec │ │  free, no key        │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ Open-Meteo   │ │  ipify.org   │ │  Ticketmaster        │ │
│  │  (weather)   │ │ (client IP)  │ │  Discovery API v2    │ │
│  │  free, nokey │ │  free, nokey │ │  events, key req.    │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐                          │
│  │  ipinfo.io   │ │  LangSmith   │                          │
│  │ (IP→city)    │ │  (tracing)   │                          │
│  │  free basic  │ │  optional    │                          │
│  └──────────────┘ └──────────────┘                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Frontend (`ui/src/`)

#### `api/client.ts` — WebSocketClient
- Manages the WebSocket connection to `wss://backend/ws/{session_id}`
- `sendMessage(text, user_profile, user_agent, client_ip)` — all four fields sent every message
- `client_ip` field added to `Message` interface and payload
- Exponential backoff reconnection: up to 5 attempts, delays double each time

#### `hooks/useVoiceAssistant.ts`
- Resolves client public IP via `fetch('https://api.ipify.org?format=json')` on mount → stored in `clientIpRef`
- `VOICE_TIMEOUT_MS = 30_000` — named constant, 30-second auto-stop
- Orchestrates Web Speech API, WebSocket send, and speech synthesis
- `handleBackendMessage` processes `response`, `status`, `error`, and `action` message types

#### `hooks/useUserProfile.ts`
- Reads/writes profile from `localStorage`
- `addRestaurantVisit()` / `addUberTrip()` called by `App.tsx` `onAction` handler
- Profile object includes: `id`, `firstName`, `gender`, `age`, `title`, `address`, `city`, `state`, `country`

#### `App.tsx`
- **`linkifyText()`** — two-group regex converts LLM markdown to proper `<a>` tags:
  - Group 1–3: `[label](url)` → `<a>{label}</a>` (no brackets, no trailing `)`)
  - Group 4: bare `https://...` → `<a>{url}</a>`
- **Quick-action chips** — 4 buttons in single compact row (`flex-wrap: nowrap`):
  - Weather · Restaurants · Ride · Events
  - `chat-window__quickactions--compact` modifier: `padding: 5px 9px; font-size: 12px; flex-shrink: 0`
- Draggable chat window — drag zone isolated to child `div` to prevent pointer capture conflicts
- Resize handle — `pointermove`/`pointerup` on `document`, not the handle element

---

### 2. API Server (`api_server.py`)

#### WebSocket Endpoint `/ws/{session_id}`
```python
# Client IP extracted at connection time — before any message is processed
client_ip = (
    websocket.headers.get("x-forwarded-for", "").split(",")[0].strip()
    or websocket.headers.get("x-real-ip", "")
    or (websocket.client.host if websocket.client else None)
) or None
```
- Render's load balancer sets `X-Forwarded-For` automatically
- `client_ip` passed into every `assistant.process_request()` call
- `ws_sender` injected per request for action message pushback; cleared on disconnect

#### Message Handling
```
{ type: "chat", message, user_profile, client_ip, user_agent }
    ↓
process_request(message, user_agent, user_profile, client_ip)
    ↓
{ type: "response", message, success }
{ type: "action", action, data }   ← from save tools
```

---

### 3. Agent Orchestration (`agent/core.py`)

#### AgenticAssistant
- Singleton initialized at server startup
- `process_request(user_input, user_agent, user_profile, client_ip)` — single entry point
- Stores `client_ip` on both `location_adapter._client_ip` and `location_service._client_ip` before any tool runs
- Injects `[SYSTEM CONTEXT — User location: Erie, PA]` hint into every agent prompt

#### LocationContextAdapter
Wraps `ContextManager` + `LocationService` into a single interface for all tools:

```python
class LocationContextAdapter:
    def get_location(self):
        return self._ctx.get_location()           # ContextManager path

    def get_current_location(self, client_ip=None):
        loc = self._ctx.get_location()
        if loc and (loc.get("latitude") or loc.get("city")):
            return loc                             # profile location wins
        return self._fallback.get_current_location(client_ip=client_ip)  # client IP fallback
```

#### `_extract_location_from_profile()`
```python
# Builds geocodable query from profile fields
geocode_query = f"{city}, {state}"   # e.g. "Erie, PENNSYLVANIA"
time.sleep(1.1)                       # Nominatim rate-limit pre-sleep
lat, lon = RestaurantFinder._geocode_city(geocode_query)
context_manager.set_location({latitude: lat, longitude: lon, city, state, ...})
```

#### LangChain Agent Setup
```python
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, tools=tools,
    verbose=True,
    max_iterations=10,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
)
```

---

### 4. Tool Layer (`src/tools/`)

#### `base.py` — BaseTool
Abstract base: `validate → execute → handle_error`. All tools inherit this. `handle_error` returns `{"success": False, "error": str(e), "tool": self.name}`.

#### `restaurant_finder.py` — RestaurantFinder
- **Data:** Overpass API (OpenStreetMap) — free, no key
- **Geocoding:** Nominatim — free; 1 req/sec policy enforced
- **Schema:** `location: Union[str, dict, None]` — LLM may pass string or dict; normalized internally
- **Location resolution order:**
  1. Explicit dict with `lat`/`lon` or `latitude`/`longitude`
  2. Explicit string city name → `_geocode_city()`
  3. `LocationContextAdapter._coords_from_service()` → profile coords
  4. `_profile_address_from_service()` → geocode profile address string
  5. Client IP → `ipinfo.io` geolocate
  6. `_get_location_from_ip()` (final fallback)

- **`_geocode_city()` — rate limit handling:**
```python
max_retries = 3
for attempt in range(max_retries):
    time.sleep(1.1 * (attempt + 1))       # 1.1s, 2.2s, 3.3s
    try:
        # Nominatim request
    except urllib.error.HTTPError as e:
        if e.code == 429 and attempt < max_retries - 1:
            time.sleep(2 ** (attempt + 1)) # 2s, 4s backoff
            continue
        raise
```

#### `weather.py` — WeatherTool
- Open-Meteo API — free, no key, no rate limit concerns
- Coordinates from `LocationContextAdapter`

#### `uber.py` — UberTool
- Generates `https://m.uber.com/ul/?action=setPickup&...` deep link
- Pickup: profile address geocoded (desktop context) / GPS (mobile context)
- `user_agent` inspected to detect mobile vs desktop

#### `events.py` — EventsTool *(new in v2.0)*
- **API:** Ticketmaster Discovery API v2
- **Auth:** `TICKETMASTER_API_KEY` in `config/.env`
- **Date window:** `now → now + timedelta(days=30)` — always computed dynamically
- **Sort:** `date,asc` — soonest events first
- **Minimum 10 results:** `display_limit = max(10, int(limit))` — LLM cannot return fewer
- **No image fields:** `image_url` removed from `_parse_events()` return — prevents `![Image](url)` in chat
- **State normalisation:** `_state_to_code("PENNSYLVANIA")` → `"PA"`
- **Keyword → segment ID mapping:**

| Keyword | Ticketmaster Segment ID |
|---------|------------------------|
| music, concert | `KZFzniwnSyZfZ7v7nJ` |
| sports, sport | `KZFzniwnSyZfZ7v7nE` |
| arts, theatre, comedy | `KZFzniwnSyZfZ7v7na` |
| family, miscellaneous | `KZFzniwnSyZfZ7v7n1` |
| film | `KZFzniwnSyZfZ7v7nn` |

#### `save_preferences_tool.py` — SaveRestaurantTool / SaveUberTripTool
- Called by agent when user asks to save/remember a restaurant or trip
- Uses injected `ws_sender` to push `{"type": "action", "action": "save_restaurant", "data": {...}}` over WebSocket
- Frontend `onAction` handler in `App.tsx` persists to `localStorage`
- `ws_sender` cleared when WebSocket closes to avoid stale references

---

### 5. Service Layer (`src/services/`)

#### `services/location.py` — LocationService
```python
def get_current_location(self, client_ip: Optional[str] = None) -> dict:
    ip_target = client_ip if client_ip else 'me'
    # 'me' = server IP → wrong on cloud deployments
    # client_ip = browser's real public IP → correct
    g = geocoder.ip(ip_target)
    ...
```
- `geocode_address()` — Nominatim with multiple address format variants + ZIP/city fallback
- `reverse_geocode()` — coordinates → address string
- `get_distance()` — Haversine formula
- `_geocode_cache` — dict cache to avoid repeated identical Nominatim calls

#### `services/context.py` — ContextManager
- `set_location(dict)` — stores geocoded coordinates for the session
- `get_location()` → `{"latitude", "longitude", "city", "state", "address", "source"}`
- `add_to_history(role, content)` — conversation history (capped at last N turns)
- `get_history(limit)` — returns recent turns for LLM context window
- `extract_preferences_from_interaction()` — detects cuisine preferences, destinations from conversation

---

## Location Resolution — End-to-End Trace

This is the most critical system behaviour. The full pipeline for a request from SAI KIRAN in Erie, PA while the backend runs in Columbus, OH:

```
1. BROWSER MOUNT
   useVoiceAssistant: fetch('https://api.ipify.org') → clientIpRef = "24.210.110.237"

2. MESSAGE SENT
   WebSocket payload: {
     message: "find a restaurant near me",
     user_profile: { city: "Erie", state: "PENNSYLVANIA", address: "5013 Burgundy Dr" },
     client_ip: "24.210.110.237"
   }

3. API SERVER (Render, Columbus OH)
   X-Forwarded-For: "24.210.110.237"   ← set by Render load balancer
   client_ip = "24.210.110.237"
   → process_request(message, user_profile, client_ip="24.210.110.237")

4. CORE.PY
   location_adapter._client_ip = "24.210.110.237"
   location_service._client_ip = "24.210.110.237"
   
   _extract_location_from_profile(user_profile):
     geocode_query = "Erie, PENNSYLVANIA"
     time.sleep(1.1)
     lat, lon = RestaurantFinder._geocode_city("Erie, PENNSYLVANIA")
     → Nominatim → (42.1292, -80.0851)   ← Erie, PA ✅
     context_manager.set_location({latitude: 42.1292, longitude: -80.0851, city: "Erie"})

5. AGENT PROMPT
   "[SYSTEM CONTEXT — User location: Erie, PENNSYLVANIA. Always use this location...]"

6. TOOL CALL
   search_restaurants(query="restaurant")
   _resolve_location(None)
   → _coords_from_service → ctx.get_location() → (42.1292, -80.0851)   ← Erie ✅

7. OVERPASS QUERY
   Centred on (42.1292, -80.0851), radius 3000m → restaurants in Erie, PA ✅

8. RESPONSE
   "I found 5 restaurants near you in Erie, PA..."
   → linkifyText() renders any markdown links as clean <a> tags
   → spoken via Speech Synthesis
```

---

## Data Flow Examples

### Restaurant Search
```
User: "Find Italian restaurants near me"
    ↓
search_restaurants(query="italian", location=None)
    ↓
_resolve_location → profile coords (42.13, -80.09)
    ↓
Overpass API: [amenity=restaurant][cuisine~"italian"] within 3000m
    ↓
_parse_results → sorted by distance
    ↓
{ success: True, count: 5, restaurants: [...] }
```

### Events Discovery
```
User: "What events are happening near me this month?"
    ↓
find_local_events(city="Erie", state_code="PA")
    ↓
now = UTC now; end = now + 30 days
Ticketmaster: countryCode=US, stateCode=PA, city=Erie, sort=date,asc, size=20
    ↓
_parse_events: name, date, venue, address, category, price, url  (no image_url)
display_limit = max(10, limit)  → top 10
    ↓
LLM: "1. [Event Name](https://ticketmaster.com/...) at Venue on Date"
    ↓
linkifyText → <a>Event Name</a>  ← no trailing )
```

### Uber Booking
```
User: "Book an Uber to the airport"
    ↓
book_uber_ride(destination="Erie International Airport")
    ↓
pickup = profile address ("5013 Burgundy Dr, Erie, PA")
       → Nominatim → (42.1292, -80.0851)
destination = "Erie International Airport"
            → Nominatim → (42.0831, -80.1739)
    ↓
https://m.uber.com/ul/?action=setPickup&pickup[lat]=42.1292&pickup[lng]=-80.0851
  &dropoff[lat]=42.0831&dropoff[lng]=-80.1739&...
    ↓
SaveUberTripTool → ws_sender → { type: "action", action: "save_uber_trip", data: {...} }
    ↓
App.tsx onAction → addUberTrip() → localStorage
```

### Save Action Pipeline
```
Backend tool → ws_sender(JSON string)
    ↓
WebSocket message: { type: "action", action: "save_restaurant", data: { name, address, ... } }
    ↓
useVoiceAssistant: onActionRef.current({ action, data })
    ↓
App.tsx onAction switch → addRestaurantVisit(data)
    ↓
useUserProfile → localStorage.setItem(...)
```

---

## Nominatim Rate Limiting Strategy

Nominatim enforces a strict 1 request/second policy. The system handles this at two levels:

**Level 1 — Profile geocode (core.py):**
```python
time.sleep(1.1)                              # pre-sleep before first call
lat, lon = RestaurantFinder._geocode_city(geocode_query)
```

**Level 2 — Tool geocode (restaurant_finder.py):**
```python
for attempt in range(3):
    time.sleep(1.1 * (attempt + 1))          # 1.1s, 2.2s, 3.3s pre-sleep
    try:
        result = nominatim_request(url)
        return result
    except HTTPError as e:
        if e.code == 429:
            time.sleep(2 ** (attempt + 1))   # 2s, 4s on 429
            continue
        raise
```

This staggers the profile geocode (fires first) and the restaurant/event geocode (fires at least 1.1s later), ensuring the two never collide against Nominatim's rate limit.

---

## Design Patterns

### 1. Atomic Tool Pattern
Each tool is a self-contained, independently testable unit with single responsibility. Tools accept `location_service` at construction time for location access, never importing it directly.

### 2. LocationContextAdapter Pattern
A single adapter wraps `ContextManager` (profile location) + `LocationService` (IP/GPS fallback) and presents one `get_current_location()` interface to all tools. This enforces the priority chain at one point rather than duplicating logic across tools.

### 3. Context Injection Pattern
User location and profile are injected as a `[SYSTEM CONTEXT]` prefix into the agent's `input` string on every invocation — not baked into the system prompt at startup. This ensures the LLM always uses current per-request values, not stale startup state.

### 4. WebSocket Action Pattern
Tools that need to persist data to the frontend (save restaurant, save trip) push `{"type": "action", ...}` messages via an injected `ws_sender` callable rather than returning data in the tool result. The frontend `onAction` handler in `App.tsx` receives and persists these to `localStorage`. This keeps backend tools decoupled from frontend storage.

### 5. Client IP Pipeline Pattern
Client IP flows from `api.ipify.org` (browser) → WebSocket payload → HTTP headers (Render/Nginx) → `process_request()` → `location_adapter._client_ip` → `location_service._client_ip` → `geocoder.ip(client_ip)`. Any layer that fails gracefully falls through to the next. Server IP is the absolute last resort and is never actually reached in normal operation.

---

## Error Handling

### Tool Level
```python
def execute(self, ...):
    try:
        return {"success": True, "data": result}
    except Exception as e:
        return self.handle_error(e)
        # → {"success": False, "error": str(e), "tool": self.name}
```

### Location Level
```python
# Priority fallback — never raises, always returns coords
def _resolve_location(self, location):
    if isinstance(location, dict):  return extract_coords(location)
    if isinstance(location, str):   return self._geocode_city(location)
    coords = self._coords_from_service(self.location_service)
    if coords: return coords
    lat, lon, _ = self._get_location_from_ip()  # client IP via ipinfo.io
    return lat, lon
```

### Agent Level
```python
try:
    result = self.agent_executor.invoke({"input": hint + user_input, "chat_history": history})
except Exception as e:
    return {"success": False, "output": "I encountered an error. Could you rephrase?"}
```

### WebSocket Level
```typescript
this.ws.onerror = (error) => {
    if (this.hasConnectedOnce) {
        setError('Connection lost. Attempting to reconnect...');
    }
    this.attemptReconnect();  // exponential backoff, max 5 attempts
};
```

---

## Monitoring & Observability

### LangSmith Integration
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=personalized-agentic-assistant
```
Traces every agent decision, tool input/output, and token count. View at https://smith.langchain.com/

### Logging Strategy (Loguru)
| Level | Examples |
|-------|---------|
| INFO | Tool calls, location resolved, events found |
| WARNING | Nominatim 429 retry, client IP fallback used, location shape mismatch |
| ERROR | API failures, tool exceptions |
| DEBUG | Full Nominatim URL (API key redacted), raw tool inputs |

### Key Log Lines to Watch
```
INFO  | [EventsTool] API returned 20 events for Erie, PA
INFO  | Geocoded user profile location 'Erie, PENNSYLVANIA' → (42.1292, -80.0851)
WARNING | Nominatim rate-limited (429) — retrying in 2s (attempt 1/3)
INFO  | Client IP geolocation: Erie, PA (42.1292, -80.0851)
```

---

## Security

| Concern | Implementation |
|---------|---------------|
| API keys | `config/.env` only; never in frontend bundle; `.gitignore` |
| Ticketmaster key | Backend only; not exposed to browser |
| User profile | `localStorage` only; never sent to third parties |
| XSS via links | `linkifyText` uses React element creation, not `dangerouslySetInnerHTML` |
| CORS | `allow_origins` restricted to known domains in production |
| HTTPS | Required in production; mic access blocked on HTTP |
| Client IP logging | Debug level only; not persisted |

---

## Configuration

### `config/config.yaml`
```yaml
agent:
  model: "gpt-4"              # or any OpenRouter model string
  temperature: 0.7
  max_iterations: 10
  use_openrouter: true

location:
  use_gps: true
  fallback_location: "New York, NY"   # last resort only

monitoring:
  langsmith_enabled: false
  log_level: "INFO"
```

### `config/.env`
```bash
OPENROUTER_API_KEY=your_openrouter_key
TICKETMASTER_API_KEY=your_ticketmaster_key
LANGCHAIN_TRACING_V2=true          # optional
LANGCHAIN_API_KEY=your_langsmith_key   # optional
LANGCHAIN_PROJECT=personalized-agentic-assistant
```

### `ui/.env`
```bash
VITE_WS_URL=wss://your-backend.onrender.com
VITE_API_URL=https://your-backend.onrender.com
```

---

## Testing

### Standalone Test Pages (no build required)
```
ui/test-speech-recognition.html  — Web Speech API mic test
ui/stop-speaking-demo.html       — Speech synthesis / TTS test
ui/websocket-debugger.html       — WebSocket connection debugger
```

### Backend Test
```bash
python test_backend.py
curl http://localhost:8000/health
```

### Critical Test Cases
| Test | Pass Criteria |
|------|--------------|
| Location pipeline | Backend logs show Erie, PA coordinates, not Columbus, OH |
| Events minimum | Response always contains ≥10 events |
| Link rendering | No `[`, `]`, `(`, `)` visible in chat bubbles |
| Nominatim 429 | User sees results, not error; logs show retry |
| Voice timeout | Recording still active at 25s, stops at 30s |
| Reconnect | App reconnects automatically after backend restart |

---

## Future Enhancements

### Near-Term (v2.1)
- Toast notification system (replace `alert()`)
- FAB replacing competing CTAs
- SlideUpInput for mobile thumb zone
- Lucide React icon unification
- ARIA improvements

### Medium-Term (v3.0)
- PostgreSQL for preference persistence
- Redis caching (Nominatim, Overpass, Ticketmaster responses)
- Native iOS/Android app
- Calendar tool integration
- Progressive Web App (PWA)

### Long-Term
- Microservices decomposition for heavy tools
- Kubernetes deployment
- Plugin marketplace
- Edge/offline capability

---

**Architecture prioritizes: Profile-first location accuracy · Modularity · Testability · Extensibility · Production-Readiness**

**Version:** 2.0 — Full rewrite reflecting current production system
**Last Updated:** March 2026
