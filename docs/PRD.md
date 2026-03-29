# Product Requirements Document (PRD)
# Personalized Agentic Voice Assistant

**Version:** 2.0.0
**Date:** March 2026
**Status:** Production Ready
**Owner:** Product Team

---

## Executive Summary

### Vision
Create an intelligent, personalized voice assistant that resolves the user's real geographic location from their profile — never from the server — and executes everyday actions through natural voice or text interaction.

### Mission
Deliver a production-ready voice assistant combining AI conversation with practical, location-accurate tools for weather, restaurant discovery, event discovery, and ride booking, while keeping all personal data in the user's browser.

### Target Users
- **Primary**: Individuals wanting a single interface for local services (weather, food, rides, events)
- **Secondary**: Accessibility users requiring voice-first interfaces
- **Tertiary**: Developers extending the platform with new tool integrations

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [User Personas](#2-user-personas)
3. [User Stories](#3-user-stories)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Technical Specifications](#6-technical-specifications)
7. [User Interface](#7-user-interface)
8. [Data Flow](#8-data-flow)
9. [Security & Privacy](#9-security--privacy)
10. [Testing Strategy](#10-testing-strategy)
11. [Success Metrics](#11-success-metrics)
12. [Release Plan](#12-release-plan)
13. [Future Roadmap](#13-future-roadmap)
14. [Appendices](#14-appendices)

---

## 1. Product Overview

### 1.1 Problem Statement

**Current Pain Points:**
- Existing voice assistants lack deep integration with local services
- Cloud-hosted backends geolocate the server, not the user — returning wrong city results
- Limited personalization and context awareness
- Privacy concerns with cloud-based data storage
- Difficult to extend with custom capabilities

**Our Solution:**
A modular, privacy-first agentic voice assistant that:
- Resolves the user's real location from their saved profile address, with client IP as fallback
- Combines AI conversation with practical location-aware tools
- Stores all personal data in the user's browser (`localStorage`) — nothing on the server
- Enables easy extension with new LangChain tools
- Works seamlessly across desktop and mobile browsers

### 1.2 Core Technical Problem Solved (v2.0)

The original v1.0 deployed backend on Render (Columbus, Ohio). All location-aware queries — restaurants, weather, events, Uber — returned results for Columbus rather than the user's actual city (Erie, PA).

**Root cause:** `geocoder.ip('me')` on the server always resolves to the server's IP.

**v2.0 solution — four-layer location pipeline:**
```
1. Profile has lat/lon coords     → use directly
2. Profile has address/city/state → Nominatim geocode → use
3. Client IP sent from browser    → ipinfo.io geolocate → use
4. Server IP                      → NEVER used
```

This required coordinated changes across 6 files: `useVoiceAssistant.ts`, `client.ts`, `api_server.py`, `agent/core.py`, `services/location.py`, and `tools/restaurant_finder.py`.

### 1.3 Value Proposition

**For End Users:**
- 🎯 **Location-Accurate**: Results always for YOUR city, not the server's city
- 🗣️ **Natural**: Conversational AI via OpenRouter/OpenAI
- 📍 **Profile-First**: Saves your address once; used automatically for all tools
- 🎟️ **Events Discovery**: Upcoming local events via Ticketmaster
- 🔒 **Private**: Profile data in your browser only

**For Developers:**
- 🔧 **Modular**: Add new tools with minimal boilerplate
- 📚 **Well-Documented**: CLAUDE.md, README, ARCHITECTURE, PRD, SIMPLE_GUIDE
- 🚀 **Production-Ready**: FastAPI + React + WebSocket stack
- 📊 **Observable**: LangSmith integration for full agent trace visibility

### 1.4 Competitive Analysis

| Feature | Our Product | Alexa | Google Assistant | Siri |
|---------|-------------|-------|-----------------|------|
| Open Source | ✅ | ❌ | ❌ | ❌ |
| Local Data Storage | ✅ | ❌ | ❌ | ❌ |
| Custom Tools | ✅ Easy | ⚠️ Complex | ⚠️ Complex | ❌ |
| AI Model Choice | ✅ Any via OpenRouter | ❌ Fixed | ❌ Fixed | ❌ Fixed |
| Profile-First Location | ✅ | ❌ | ❌ | ❌ |
| Local Events Tool | ✅ Ticketmaster | ⚠️ Basic | ⚠️ Basic | ❌ |
| Uber Integration | ✅ Smart pickup | ⚠️ Basic | ⚠️ Basic | ⚠️ Basic |
| Web-Based | ✅ | ❌ | ❌ | ❌ |
| Privacy-First | ✅ | ❌ | ❌ | ❌ |
| Free Data APIs | ✅ OSM/Open-Meteo | ❌ | ❌ | ❌ |

---

## 2. User Personas

### Persona 1: "SAI KIRAN" (Reference User / Primary Persona)

**Demographics:**
- Age: 39, Male
- Location: Erie, Pennsylvania
- Device: Windows desktop (Chrome) + mobile
- Tech proficiency: Advanced

**Goals:**
- Get restaurant recommendations for Erie, PA — not Columbus, OH
- Check local weather, discover upcoming events
- Book Uber from home address without re-entering it

**Pain Points (pre-v2.0):**
- Backend server in Columbus returned Columbus results
- Had to re-specify city on every query

**How v2.0 Helps:**
- Profile address (`5013 Burgundy Dr, Erie, PENNSYLVANIA`) geocoded on every request
- All tools — restaurants, weather, events, Uber — use Erie, PA automatically
- Events chip shows Ticketmaster events in Erie/PA area

---

### Persona 2: "Tech-Savvy Taylor"

**Demographics:**
- Age: 28, Software Engineer, Urban area
- Tech proficiency: Advanced

**Goals:**
- Automate daily tasks (weather, ride booking, finding events)
- Quick access to local information
- Extend platform with custom tools

**How Our Product Helps:**
- Voice-first interface + text input fallback
- Direct integrations (Uber, weather, restaurants, events)
- Open architecture — add tools by creating one file and one registration line

---

### Persona 3: "Busy Professional Blake"

**Demographics:**
- Age: 35, Marketing Manager, Urban area

**Goals:**
- Single interface for weather, dining, rides, events
- Minimal app switching
- Quick-action chips for most common queries

**How Our Product Helps:**
- 4 quick-action chips in a single compact row: Weather · Restaurants · Ride · Events
- One click triggers the right tool with no typing
- Profile stored so no repeated setup

---

### Persona 4: "Accessibility-Focused Alex"

**Demographics:**
- Age: 45, Accountant, Suburban area
- Moderate tech proficiency, visual impairment

**Goals:**
- Independent task completion via voice
- Screen-reader compatible interface

**How Our Product Helps:**
- Voice-first interaction with 30-second timeout (no rush)
- Text input alternative for non-voice usage
- Keyboard navigation throughout

---

## 3. User Stories

### Epic 1: Voice Interaction

#### Story 1.1: Push-to-Talk
**As a** user
**I want to** hold the mic button to speak
**So that** I control exactly when the assistant listens

**Acceptance Criteria:**
- [x] Hold mic button → microphone activates
- [x] Visual pulse rings indicate listening state
- [x] Release button → speech sent automatically
- [x] Works on Chrome and Edge

---

#### Story 1.2: Manual Stop
**As a** user
**I want to** click once and speak freely
**So that** I can compose longer queries

**Acceptance Criteria:**
- [x] Single click starts listening
- [x] "Stop & Send" button appears
- [x] Click Stop & Send → sends transcript
- [x] 30-second auto-timeout as safety net

---

#### Story 1.3: Auto-Timeout
**As a** user
**I want** automatic cutoff after silence
**So that** I'm never stuck in listening state

**Acceptance Criteria:**
- [x] `VOICE_TIMEOUT_MS = 30_000` (30 seconds)
- [x] Timeout clears and sets status to idle
- [x] Error message shown briefly, then clears

---

#### Story 1.4: Text Input
**As a** user who prefers typing
**I want** a text input alongside voice
**So that** I can use the assistant in noisy environments or non-Chrome browsers

**Acceptance Criteria:**
- [x] Text input field visible at all times
- [x] Enter key submits message
- [x] Disabled during processing
- [x] Works in all modern browsers

---

### Epic 2: User Profiles & Location

#### Story 2.1: Profile Setup
**As a** new user
**I want to** set up my profile on first launch
**So that** all tools know my city and name

**Acceptance Criteria:**
- [x] 3-step wizard on first visit (name → demographics → address)
- [x] All fields optional with skip option
- [x] Data saved to `localStorage`
- [x] Accessible via "Edit Profile" at any time

---

#### Story 2.2: Profile-First Location
**As a** user in Erie, PA
**I want** the assistant to use MY city for all searches
**So that** I never get results for the server's location (Columbus, OH)

**Acceptance Criteria:**
- [x] Profile address geocoded on every request via Nominatim
- [x] Client IP sent from browser as fallback
- [x] Server IP (`geocoder.ip('me')`) never used as final source
- [x] Backend logs confirm Erie, PA coordinates used

---

#### Story 2.3: Smart Uber Pickup
**As a** desktop user
**I want** Uber to pre-fill my home address as pickup
**So that** I don't have to re-enter it every time

**Acceptance Criteria:**
- [x] Profile includes street address field
- [x] Desktop: profile address used as Uber pickup
- [x] Mobile: current GPS location used instead
- [x] Falls back to city if address not saved

---

### Epic 3: Location-Aware Tools

#### Story 3.1: Weather
**As a** user
**I want to** ask about local weather
**So that** I can plan my day

**Acceptance Criteria:**
- [x] "What's the weather?" → Open-Meteo API for user's city
- [x] No API key required
- [x] Shows temperature, conditions, forecast
- [x] Weather chip triggers instantly

---

#### Story 3.2: Restaurant Search
**As a** user
**I want to** find restaurants near me
**So that** I can decide where to eat

**Acceptance Criteria:**
- [x] Results for user's actual city (Erie, PA)
- [x] Free Overpass API (OpenStreetMap) — no paid key
- [x] Sorted by distance, nearest first
- [x] Returns name, address, phone, hours, cuisine
- [x] Nominatim 429 handled with retry/backoff

---

#### Story 3.3: Uber Booking
**As a** user
**I want to** book a ride with one click
**So that** I can get transportation quickly

**Acceptance Criteria:**
- [x] Generates Ticketmaster deep link `https://m.uber.com/ul/?...`
- [x] Pickup pre-filled from profile address
- [x] Destination geocoded from query text
- [x] Link opens Uber with everything pre-filled

---

#### Story 3.4: Local Events Discovery
**As a** user
**I want to** discover upcoming events in my city
**So that** I know what's happening near me this month

**Acceptance Criteria:**
- [x] Ticketmaster Discovery API v2
- [x] 30-day window computed dynamically (never hardcoded)
- [x] Returns top 10 events (minimum enforced — LLM cannot return fewer)
- [x] Fields: name, date, venue, address, category, price, direct URL
- [x] No image fields (prevents `![Image](url)` rendering in chat)
- [x] Events quick-action chip in UI
- [x] Keyword filtering: "concerts", "sports", "theatre", etc.
- [x] State name normalised: `PENNSYLVANIA` → `PA`

---

### Epic 4: Chat UI & Link Rendering

#### Story 4.1: Markdown Link Rendering
**As a** user
**I want** event and restaurant links to render as clickable text
**So that** I don't see raw `[text](url)` syntax or broken URLs with trailing `)`

**Acceptance Criteria:**
- [x] `[Event Name](https://...)` → renders as `<a>Event Name</a>`
- [x] No trailing `)` in rendered links
- [x] Bare URLs also rendered as clickable links
- [x] Plain text preserved exactly as-is

---

#### Story 4.2: Quick-Action Chips
**As a** user
**I want** one-click shortcuts for common queries
**So that** I don't have to type the same phrases repeatedly

**Acceptance Criteria:**
- [x] 4 chips: Weather · Restaurants · Ride · Events
- [x] All 4 visible in a single row (no wrapping)
- [x] Compact layout at default 380px window width
- [x] Disabled when WebSocket disconnected
- [x] Each triggers correct tool via `sendTextMessage`

---

### Epic 5: Reliability & Error Handling

#### Story 5.1: Nominatim Rate Limit Recovery
**As a** user
**I want** location lookups to succeed even when geocoding is rate-limited
**So that** I never see a raw "429" error

**Acceptance Criteria:**
- [x] `_geocode_city()` sleeps 1.1s before each attempt
- [x] Catches HTTP 429 and retries up to 3× with 2s/4s backoff
- [x] Profile geocode staggered 1.1s before restaurant search geocode
- [x] User sees normal results, not error messages

---

#### Story 5.2: WebSocket Reconnection
**As a** user
**I want** the app to reconnect automatically if connection drops
**So that** I don't have to refresh the page

**Acceptance Criteria:**
- [x] Up to 5 reconnect attempts with exponential backoff
- [x] Connection banner shown while reconnecting
- [x] Manual "Retry" button available
- [x] Session resumes after reconnect

---

## 4. Functional Requirements

### 4.1 Location Resolution (P0 — Critical)

| Requirement | Implementation |
|-------------|---------------|
| Profile address geocoding | Nominatim geocodes `city + state` on every request |
| Client IP fallback | `api.ipify.org` resolves client IP on mount; sent in every WS message |
| Server IP prohibition | `geocoder.ip('me')` must never be the final location source |
| Nominatim rate limiting | 1.1s pre-sleep + 3× retry with 2s/4s backoff on HTTP 429 |
| Location priority order | profile lat/lon → geocode address → client IP → config fallback |

### 4.2 Voice Interface (P0)

| Requirement | Implementation |
|-------------|---------------|
| Push-to-talk | Hold mic button → record → release → send |
| Manual stop | Click mic → "Stop & Send" button → click to send |
| Auto-timeout | `VOICE_TIMEOUT_MS = 30_000` (30 seconds) |
| Speech synthesis | All responses spoken via `SpeechSynthesisUtterance` |
| Browser support | Chrome/Edge (Web Speech API); text input fallback on others |

### 4.3 Tool Integrations (P0)

| Tool | API | Auth | Result |
|------|-----|------|--------|
| Restaurant Search | Overpass API (OSM) | None | Nearby restaurants sorted by distance |
| Weather | Open-Meteo | None | Current conditions for user's city |
| Uber | Deep link | None | Pre-filled Uber URL |
| Local Events | Ticketmaster Discovery v2 | `TICKETMASTER_API_KEY` | Top 10 upcoming events, 30-day window |
| Geocoding | Nominatim (OSM) | None | Address → lat/lon |

### 4.4 Chat Message Rendering (P0)

| Requirement | Implementation |
|-------------|---------------|
| Markdown links | Two-group regex: `[label](url)` → `<a>{label}</a>` |
| Bare URLs | Regex group 4: `https://...` → `<a>{url}</a>` |
| No broken `)` in URLs | Consuming entire markdown token; `)` never enters DOM |
| Plain text preserved | Left-to-right pass; non-link text untouched |

### 4.5 Events Tool Specifics (P1)

| Requirement | Implementation |
|-------------|---------------|
| Minimum 10 results | `display_limit = max(10, int(limit))` — floor enforced |
| No image fields | `image_url` removed from `_parse_events()` return dict |
| Dynamic date window | `now → now + timedelta(days=30)` — never hardcoded |
| Keyword → segment | "concert" → Music ID, "sports" → Sports ID, etc. |
| State normalisation | `PENNSYLVANIA` → `PA` via `_state_to_code()` |

### 4.6 WebSocket Payload (P0)

```json
{
  "type": "chat",
  "message": "string",
  "user_profile": { "city": "Erie", "state": "PENNSYLVANIA", "address": "...", ... },
  "user_agent": "string",
  "client_ip": "24.210.110.237",
  "timestamp": 1711234567890
}
```

### 4.7 User Profile (P0)

Stored in browser `localStorage`. Fields: `id`, `firstName`, `gender`, `age`, `title`, `address`, `city`, `state`, `country`, `createdAt`, `lastUpdatedAt`.

Sent with every WebSocket message. Backend geocodes `city + state` on each request and injects coordinates into `ContextManager` for the session.

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Metric | Target |
|--------|--------|
| Agent response P90 | < 5 seconds |
| Nominatim geocode | < 2 seconds (with retry handling) |
| Overpass restaurant query | < 5 seconds (30s timeout) |
| Ticketmaster events query | < 3 seconds |
| WebSocket connection | < 1 second |

### 5.2 Reliability

| Metric | Target |
|--------|--------|
| WebSocket auto-reconnect | 5 attempts, exponential backoff |
| Nominatim 429 recovery | 3 retries, 2s/4s backoff |
| Location accuracy | Correct city 100% when profile has address |
| Tool failure handling | Graceful error message, no crash |

### 5.3 Compatibility

| Platform | Voice | Text |
|----------|-------|------|
| Chrome 80+ (desktop) | ✅ | ✅ |
| Edge 80+ (desktop) | ✅ | ✅ |
| Firefox | ❌ | ✅ |
| iOS Safari | ❌ | ✅ |
| Android Chrome | ✅ | ✅ |
| Min screen width | — | 320px |

### 5.4 Security

- API keys in `config/.env` only — never in frontend bundle
- User profile in `localStorage` — never sent to third parties
- HTTPS required in production (mic access requires secure context)
- CORS restricted to known origins in production
- `TICKETMASTER_API_KEY` backend-only

---

## 6. Technical Specifications

### 6.1 Backend Stack

| Component | Technology |
|-----------|-----------|
| Runtime | Python 3.8+ |
| Framework | FastAPI + uvicorn |
| Agent | LangChain `create_tool_calling_agent` + `AgentExecutor` |
| LLM | OpenRouter (configurable) / OpenAI |
| Location | Nominatim (geocode) + ipinfo.io (IP geolocation) + geopy |
| Logging | Loguru |
| Tracing | LangSmith (optional) |

### 6.2 Frontend Stack

| Component | Technology |
|-----------|-----------|
| Framework | React 18 + TypeScript |
| Build | Vite |
| Voice | Web Speech API (recognition + synthesis) |
| State | `useState`/`useRef` + `localStorage` |
| IP Resolution | `api.ipify.org` on mount |
| Icons | Inline SVG (per component) |

### 6.3 External APIs

| API | Purpose | Auth | Cost |
|-----|---------|------|------|
| OpenRouter / OpenAI | LLM reasoning | API key | Pay per token |
| Ticketmaster Discovery v2 | Local events | API key | Free tier available |
| Overpass API (OSM) | Restaurant search | None | Free |
| Nominatim (OSM) | Geocoding | None (User-Agent req.) | Free |
| Open-Meteo | Weather | None | Free |
| ipify.org | Client IP resolution | None | Free |
| ipinfo.io | IP geolocation | None | Free (basic) |

### 6.4 Verified Frontend File Structure

```
ui/src/
├── api/client.ts               # WebSocket client; sends client_ip
├── components/
│   ├── core/Button/
│   ├── ProfileSettings/
│   ├── ProfileSetup/
│   └── voice/VoiceButton/
├── hooks/
│   ├── useUserProfile.ts
│   └── useVoiceAssistant.ts    # client IP resolved on mount
├── styles/
│   ├── global.css
│   └── tokens.css
├── types/userProfile.ts
├── App.css                     # quickactions compact styles
└── App.tsx                     # linkifyText + 4 chips
```

---

## 7. User Interface

### 7.1 Chat Window

- Draggable, resizable floating window (default 380×480px)
- Minimize / maximize controls
- Drag zone isolated from control buttons (pointer capture fix applied)
- Resize handle attaches `pointermove`/`pointerup` to `document`

### 7.2 Quick-Action Chips

Four chips in a **single compact row** — no wrapping at default width:

```
[ ☀ Weather ]  [ 🍴 Restaurants ]  [ 🚗 Ride ]  [ 📅 Events ]
```

CSS: `flex-wrap: nowrap; overflow-x: auto` with `.chat-window__quickactions--compact` modifier on buttons (`padding: 5px 9px; font-size: 12px; flex-shrink: 0`).

### 7.3 Message Rendering

Assistant messages render via `linkifyText()`:
- `[Event Name](https://ticketmaster.com/...)` → `<a>Event Name</a>` (no brackets, no `)`)
- `https://bare-url.com` → `<a>https://bare-url.com</a>`
- All other text rendered as plain text nodes

### 7.4 Voice States

| State | Visual |
|-------|--------|
| Idle | Blue mic button |
| Listening | Pulse rings, status dot, "Listening…" title |
| Processing | Spinner, "Processing…" title |
| Speaking | Pulse rings, "Speaking…" title, Stop button |
| Error | Red state, auto-clears after 3 seconds |

---

## 8. Data Flow

### 8.1 Voice Query → Response

```
User speaks → Web Speech API → transcript
    ↓
useVoiceAssistant.sendMessage(text, profile, userAgent, clientIp)
    ↓
WebSocket payload: { message, user_profile, client_ip, user_agent }
    ↓
api_server.py: extract client_ip from X-Forwarded-For header
    ↓
AgenticAssistant.process_request(message, user_profile, client_ip)
    ↓
_extract_location_from_profile → Nominatim geocode → Erie, PA coords
    ↓
context_manager.set_location({latitude: 42.13, longitude: -80.09})
    ↓
LangChain Agent → tool selection → correct local results
    ↓
Response text (markdown links) → WebSocket → linkifyText() → <a> tags → display + speak
```

### 8.2 Events Query Flow

```
User: "What events are happening near me?"
    ↓
find_local_events(city="Erie", state_code="PA", country_code="US")
    ↓
now = datetime.now(UTC); end = now + 30 days
    ↓
Ticketmaster API: countryCode=US, stateCode=PA, city=Erie, sort=date,asc
    ↓
_parse_events() → name, date, venue, address, category, price, url (no image_url)
    ↓
display_limit = max(10, limit) → top 10 events
    ↓
LLM formats as markdown: [Event Name](https://ticketmaster.com/...)
    ↓
linkifyText() renders clean <a> tags — no trailing )
```

### 8.3 localStorage Persistence (Action Messages)

```
LangChain tool (save_restaurant / save_uber_trip)
    ↓
ws_sender → {"type": "action", "action": "save_restaurant", "data": {...}}
    ↓
Frontend onAction handler → addRestaurantVisit() / addUberTrip()
    ↓
useUserProfile → localStorage update
```

---

## 9. Security & Privacy

### 9.1 Data Storage

**In browser `localStorage` only:**
- User profile (name, address, preferences)
- Saved restaurants and Uber trips
- Theme preference

**Never stored server-side.** No database. Clearing browser data clears the profile.

### 9.2 API Key Management

- All API keys in `config/.env` (backend only)
- `TICKETMASTER_API_KEY` — backend only, never in frontend bundle
- `.env` in `.gitignore` — never committed
- Frontend never makes direct API calls to Ticketmaster, OpenRouter, etc.

### 9.3 Threat Model

| Threat | Mitigation |
|--------|-----------|
| API key exposure | Environment variables only; `.gitignore`; never in frontend |
| XSS via link rendering | `linkifyText` uses React element creation, not `dangerouslySetInnerHTML` |
| Wrong city results | Client IP pipeline; profile geocoding; server IP never used |
| CORS attacks | `allow_origins` restricted to known domains in production |
| Rate limit abuse | `slowapi` rate limiting (recommended for public deployments) |
| HTTPS interception | HTTPS required in production; mic access blocked on HTTP |

---

## 10. Testing Strategy

### 10.1 Unit Tests

**Backend:**
- Tool execution logic (restaurant, weather, events, uber)
- `_geocode_city()` retry/backoff on 429
- `LocationContextAdapter` priority chain
- `_state_to_code()` normalisation
- `_parse_events()` — no image_url field, clean URLs

**Frontend:**
- `linkifyText()` — markdown links, bare URLs, no trailing `)`
- `useVoiceAssistant` — client IP fetch, message payload
- `useUserProfile` — localStorage read/write
- Quick-action chip messages map

### 10.2 Integration Tests

**End-to-End Flows:**
- Voice input → correct city → correct results
- Events chip → Ticketmaster → 10 results rendered with clean links
- Profile setup → address saved → used in next query
- Desktop Uber → profile address as pickup
- Mobile Uber → GPS as pickup
- WebSocket disconnect → auto-reconnect → session resumes

### 10.3 User Acceptance Testing

| Scenario | Pass Criteria |
|----------|--------------|
| Ask "find restaurants near me" | Returns Erie, PA results (not Columbus, OH) |
| Click Events chip | Returns ≥10 events for Erie/PA area |
| Click event link | Opens correct Ticketmaster page (no 404, no trailing `)`) |
| Ask weather | Returns Erie weather, not server's city |
| Say "book Uber to downtown" | Generates valid deep link with profile address as pickup |
| Speak for 25 seconds | Recording still active at 25s, stops at 30s |
| Disconnect backend | App shows banner, auto-retries, reconnects |

---

## 11. Success Metrics

### 11.1 KPIs

**Location Accuracy:**
- Correct city returned: 100% when profile has address
- Nominatim 429 user-visible errors: 0% (all handled by retry)

**Tool Performance:**
- Restaurant search success rate: >85% (urban OSM coverage)
- Events tool success rate: >95% (Ticketmaster reliability)
- Events results ≥10: 100% (enforced floor)

**Technical:**
- Agent response P90: <5 seconds
- WebSocket uptime: >99.5%
- Link rendering correctness: 100% (no trailing `)`)

**User Engagement:**
- Quick-action chip usage: tracked via backend logs
- Profile completion rate: >80%
- Voice usage rate: >60%

---

## 12. Release Plan

### 12.1 Version 1.0 (March 2026) — Initial Release

**Status:** Superseded by v2.0

**Features delivered:**
- ✅ Voice recognition (push-to-talk + continuous)
- ✅ AI conversation (OpenRouter/OpenAI)
- ✅ User profiles with `localStorage` persistence
- ✅ Weather tool (Open-Meteo, free)
- ✅ Restaurant search (Overpass/OSM, free)
- ✅ Uber booking (smart desktop/mobile pickup)
- ✅ WebSocket real-time communication
- ✅ LangSmith monitoring

---

### 12.2 Version 2.0 (March 2026) — Current Release

**Status:** Production Ready ✅

**Features delivered:**
- ✅ **Location pipeline fix** — profile geocode → client IP → never server IP
- ✅ **Nominatim 429 retry** — 1.1s sleep + 3× backoff
- ✅ **Events tool** — Ticketmaster Discovery API v2, top 10, 30-day window
- ✅ **Events quick-action chip** — 4th chip in compact single-row layout
- ✅ **Markdown link rendering** — `[text](url)` → proper `<a>` tags, no trailing `)`
- ✅ **Top-10 enforcement** — `max(10, int(limit))` floor on events
- ✅ **Image field removal** — no `![Image](url)` in chat
- ✅ **30-second voice timeout** — `VOICE_TIMEOUT_MS = 30_000`
- ✅ **Voice timeout constant** — named constant replaces hardcoded value
- ✅ **Drag/resize bug fixes** — pointer capture isolation, resize on document

---

### 12.3 Version 2.1 (Q2 2026) — Planned

**Planned Features:**
- [ ] Toast notification system (replaces `alert()`)
- [ ] FAB (Floating Action Button) consolidating primary CTA
- [ ] SlideUpInput — mobile thumb-zone optimised text input
- [ ] SupportButton — help/escalation entry point
- [ ] Lucide React icon unification
- [ ] ARIA labels and skip-link improvements
- [ ] Multi-language support (Spanish, French)

---

### 12.4 Version 3.0 (Q3 2026) — Planned

**Major Features:**
- [ ] Mobile apps (iOS/Android native)
- [ ] Calendar integration (Google Calendar)
- [ ] Music control (Spotify deep links)
- [ ] PostgreSQL for preference persistence (replace localStorage)
- [ ] Redis caching for Nominatim/Overpass/Ticketmaster responses
- [ ] Progressive Web App (PWA)
- [ ] News briefing tool

---

### 12.5 Version 4.0 (Q4 2026) — Planned

**Enterprise Features:**
- [ ] Multi-user authentication
- [ ] Plugin/tool marketplace
- [ ] Admin dashboard + analytics
- [ ] White-label options
- [ ] On-premise deployment
- [ ] SSO integration

---

## 13. Future Roadmap

### Short-Term (0–3 months)
- UX audit items: Toast, FAB, SlideUpInput, SupportButton
- Lucide React icon unification
- ARIA/accessibility improvements
- Rate limiting middleware (`slowapi`) for production

### Medium-Term (3–9 months)
- Native mobile apps
- Smart home integration
- Microservices for heavy tools
- PostgreSQL preferences database
- Redis response caching

### Long-Term (9+ months)
- Custom wake word support
- Edge/offline capability
- Plugin marketplace
- Kubernetes deployment
- Federated preference sync

---

## 14. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|-----------|
| Agent | AI system using LangChain to select and call tools |
| Tool | Python function callable by the agent (weather, events, etc.) |
| Profile | User's personal info stored in browser localStorage |
| Session | Single WebSocket conversation instance |
| Context | ContextManager state — location, history, preferences |
| Geocoding | Converting address string → lat/lon coordinates |
| Deep Link | URL that opens an app with pre-filled data |
| `client_ip` | Browser's real public IP, fetched via `api.ipify.org` |
| `LocationContextAdapter` | Wraps ContextManager + LocationService; enforces location priority chain |
| Nominatim | Free OSM geocoding service; max 1 req/sec |
| Overpass API | Free OSM query API; used for restaurant search |
| `linkifyText` | Frontend function converting markdown links to `<a>` tags |

### Appendix B: References

**Internal Documentation:**
- `CLAUDE.md` — complete technical reference (v6.0)
- `ARCHITECTURE.md` — system diagrams and component detail
- `SIMPLE_GUIDE.md` — user-facing plain-English guide
- `README.md` — developer quickstart

**External APIs:**
- Ticketmaster Discovery API v2: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
- Overpass API: https://overpass-api.de/
- Nominatim: https://nominatim.org/release-docs/latest/api/Search/
- Open-Meteo: https://open-meteo.com/en/docs
- LangChain: https://docs.langchain.com
- FastAPI: https://fastapi.tiangolo.com
- Web Speech API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

### Appendix C: Change Log

| Version | Date | Key Changes |
|---------|------|-------------|
| v2.0.0 | Mar 2026 | Location pipeline fix (profile→geocode→client IP); Events tool (Ticketmaster); markdown link rendering fix; 4-chip compact row; top-10 enforcement; image field removed; 30s voice timeout; drag/resize fixes |
| v1.0.0 | Mar 2026 | Initial production release: voice, weather, restaurants, Uber, profiles, WebSocket |
| v0.9.0 | Feb 2026 | Beta: profile system, theme selector, accessibility |
| v0.5.0 | Jan 2026 | Alpha: basic voice recognition, weather, restaurant tools |

---

**Document Version:** 2.0.0
**Last Updated:** March 2026
**Next Review:** June 2026

---

**Approval Signatures:**

Product Manager: ________________
Engineering Lead: ________________
Design Lead: ________________
QA Lead: ________________
