# Personalized Agentic Voice Assistant — Frontend

React 18 + TypeScript + Vite frontend for the voice-first AI assistant. Communicates with the FastAPI backend over WebSocket, resolves the user's public IP via ipify.org, and renders the full chat + voice UI.

---

## Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Framework | React 18 + TypeScript |
| Build tool | Vite 5 |
| Voice input | Web Speech API — browser-native (Chrome/Edge) |
| Voice output | Speech Synthesis API — browser-native TTS |
| Transport | WebSocket (`api/client.ts`) |
| Animation | Framer Motion |
| Persistence | localStorage (profile, restaurant visits, Uber trips) |
| Styling | CSS custom properties (`tokens.css`) |

---

## Quick Start

```bash
npm install
npm run dev        # → http://localhost:5173
```

### Scripts

| Command | Description |
| ------- | ----------- |
| `npm run dev` | Start Vite dev server on port 5173 |
| `npm run build` | TypeScript check + production build → `dist/` |
| `npm run preview` | Preview production build locally |
| `npm run lint` | ESLint check (zero warnings policy) |
| `npm run type-check` | TypeScript check without emitting |

### Environment

Create `ui/.env` (or set in Render Static Site dashboard):

```bash
VITE_WS_URL=wss://your-backend.onrender.com
VITE_API_URL=https://your-backend.onrender.com
```

In development, omit these and the app defaults to `ws://localhost:8000`.

---

## File Structure

```text
ui/
├── src/
│   ├── api/
│   │   └── client.ts               # WebSocket client; client_ip in every payload
│   ├── components/
│   │   ├── core/
│   │   │   └── Button/
│   │   │       ├── Button.tsx
│   │   │       └── Button.css
│   │   ├── ProfileSetup/
│   │   │   ├── ProfileSetup.tsx    # 3-step onboarding modal
│   │   │   └── ProfileSetup.css
│   │   ├── ProfileSettings/
│   │   │   ├── ProfileSettings.tsx # Edit profile + danger zone (reset)
│   │   │   └── ProfileSettings.css
│   │   └── voice/VoiceButton/
│   │       ├── VoiceButton.tsx     # Push-to-talk with waveform animation
│   │       └── VoiceButton.css
│   ├── hooks/
│   │   ├── useVoiceAssistant.ts    # Voice + WebSocket + ipify + TTS orchestration
│   │   └── useUserProfile.ts       # Profile state + localStorage persistence
│   ├── styles/
│   │   ├── tokens.css              # Design token system (colors, spacing, type)
│   │   └── global.css              # Base reset and global styles
│   ├── types/
│   │   └── userProfile.ts          # UserProfile, RestaurantVisit, UberTrip types
│   ├── App.css                     # Chat window + quick actions layout
│   ├── App.tsx                     # Root — linkifyText, 4 chips, drag/resize
│   └── main.tsx                    # React entry point
├── _redirects                      # SPA routing (Render / Netlify / Cloudflare)
├── .env                            # VITE_WS_URL, VITE_API_URL
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── test-speech-recognition.html    # Standalone mic test (no build needed)
├── stop-speaking-demo.html         # Standalone TTS test (no build needed)
└── websocket-debugger.html         # Standalone WebSocket debugger
```

---

## Key Modules

### `api/client.ts` — WebSocketClient

Manages the WebSocket connection to `ws://localhost:8000/ws/{session_id}` (or `wss://` in production).

```typescript
sendMessage(text: string, userProfile: UserProfile, userAgent: string, clientIp: string): void
```

- Sends `{ type, message, user_profile, client_ip, user_agent, timestamp }` on every message
- Exponential backoff reconnect — up to 5 attempts, delay doubles each time
- Handles `response`, `status`, `error`, and `action` message types from the server

### `hooks/useVoiceAssistant.ts`

Central orchestration hook — Voice + WebSocket + TTS in one place.

```typescript
const {
  status,          // 'idle' | 'listening' | 'processing' | 'speaking' | 'error'
  conversation,    // ConversationMessage[]
  isConnected,
  isConnecting,
  error,
  startListening,
  stopListening,
  stopSpeaking,
  sendTextMessage,
  clearConversation,
  reconnect,
} = useVoiceAssistant({ backendUrl, userProfile, onAction });
```

**Key behaviours:**

- Fetches client public IP via `fetch('https://api.ipify.org?format=json')` on mount → stored in `clientIpRef`; included in every WebSocket payload
- `VOICE_TIMEOUT_MS = 30_000` — auto-stops recording after 30 seconds
- `onAction` callback receives `{ action: "save_restaurant" | "save_uber_trip", data }` pushed from the backend; `App.tsx` persists these to localStorage

### `hooks/useUserProfile.ts`

Profile state backed by localStorage.

```typescript
const {
  isProfileSetup,        // boolean — drives ProfileSetup modal
  profile,               // UserProfile | null
  getGreeting,           // () => string
  updateProfile,         // (partial: Partial<UserProfile>) => void
  resetUserData,         // () => void — clears all localStorage
  addRestaurantVisit,    // (visit: RestaurantVisit) => void
  addUberTrip,           // (trip: UberTrip) => void
} = useUserProfile();
```

Profile shape (`types/userProfile.ts`):

```typescript
interface UserProfile {
  id: string;
  firstName: string;
  lastName?: string;
  gender?: string;
  age?: number;
  title?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  createdAt: string;
  lastUpdatedAt: string;
}
```

### `App.tsx` — Root Component

- **`linkifyText()`** — two-group regex converts LLM markdown to proper `<a>` tags:
  - `[label](url)` → `<a>label</a>` (no brackets, no trailing `)`)
  - Bare `https://...` → `<a>url</a>`
- **4 quick-action chips** in a single compact row (`flex-wrap: nowrap`): Weather · Restaurants · Ride · Events
- **Draggable chat window** — drag isolated to header child `div` to prevent pointer-capture conflicts with buttons
- **Resizable chat window** — `pointermove`/`pointerup` listeners on `document` to avoid losing events at edge
- **Theme selector** — `light | dark | high-contrast` via `data-theme` on `<html>`

---

## Components

### `VoiceButton`

The primary interaction element.

```tsx
<VoiceButton
  status="idle" | "listening" | "processing" | "speaking" | "error"
  onPointerDown={() => startListening()}
  onPointerUp={() => stopListening()}
  onClick={() => { /* toggle manual mode */ }}
  disabled={!isConnected}
/>
```

Visual states:

| Status | Visual |
| ------ | ------ |
| `idle` | Static, primary colour |
| `listening` | Pulsing blue, waveform rings |
| `processing` | Rotating gradient |
| `speaking` | Gentle glow, animated sound bars |
| `error` | Red, shake animation |

### `ProfileSetup`

3-step onboarding modal shown on first visit:

1. Name (`firstName`, `lastName`)
2. Personal info (`gender`, `age`, `title`)
3. Location (`address`, `city`, `state`, `country`)

### `ProfileSettings`

In-session profile editor with a **Danger Zone** section that calls `resetUserData()` to wipe localStorage.

### `Button`

General-purpose button with variants: `primary | secondary | ghost | danger`, sizes `sm | base | lg | xl`, and `loading` / `disabled` states.

---

## Design Tokens (`styles/tokens.css`)

All visual decisions are tokenised:

```css
/* Colors */
--color-primary-500: #0ea5e9;
--color-success:     #10b981;
--color-error:       #ef4444;
--text-primary:      #111827;
--background:        #ffffff;

/* Spacing — 8-point grid */
--space-2: 0.5rem;   /* 8px  */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */

/* Typography */
--text-base: 1rem;
--text-lg:   1.125rem;
--font-display: -apple-system, system-ui;

/* Touch targets */
--touch-min:      48px;
--height-button:  48px;

/* Motion */
--ease-out:      cubic-bezier(0, 0, 0.2, 1);
--duration-base: 250ms;
```

Themes (`data-theme` on `<html>`): `light` (default) · `dark` · `high-contrast`.

---

## Voice Interaction Modes

| Mode | How to use | Timeout |
| ---- | ---------- | ------- |
| Push-to-talk | Hold `VoiceButton` → speak → release | — |
| Manual stop | Click `VoiceButton` → speak → click **Stop & Send** | — |
| Auto-timeout | Click `VoiceButton` → speak → auto-sends | 30 s |

**Browser support:** Chrome and Edge only (Web Speech API).
HTTPS is required in production; `http://localhost` works in development.

---

## Standalone Test Pages

No build step required — open directly in a browser:

| File | Purpose |
| ---- | ------- |
| `test-speech-recognition.html` | Test Web Speech API microphone access |
| `stop-speaking-demo.html` | Test Speech Synthesis TTS playback |
| `websocket-debugger.html` | Inspect WebSocket frames against the backend |

---

## Deployment

### Render Static Site

- **Build command:** `cd ui && npm run build`
- **Publish directory:** `ui/dist`
- **Environment variable:** `VITE_WS_URL=wss://your-backend.onrender.com`

`_redirects` handles SPA routing so deep-linked URLs don't 404:

```
/* /index.html 200
```

### Netlify / Cloudflare Pages

Same build and publish settings. `_redirects` is respected by both platforms.

---

## Troubleshooting

| Symptom | Fix |
| ------- | --- |
| Voice button does nothing | Chrome/Edge only; grant mic permission; HTTPS in production |
| WebSocket "Disconnected" | Confirm backend is running: `curl http://localhost:8000/health` |
| Wrong city in tool results | Check profile has `city` and `state` set in ProfileSettings |
| Links show brackets/`)` | Ensure `App.tsx` uses the two-group `LINK_RE` regex in `linkifyText()` |
| Quick-action chips wrap | `.chat-window__quickactions--compact` modifier must be applied |

---

## Related Documentation

| Document | Purpose |
| -------- | ------- |
| [../README.md](../README.md) | Root project overview — full stack quick start |
| [../CLAUDE.md](../CLAUDE.md) | Complete codebase and engineering reference |
| [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) | System design and data flow traces |
| [../docs/DIAGRAMS.md](../docs/DIAGRAMS.md) | Mermaid diagrams for all flows |
| [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) | Full design token and component reference |
| [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) | Backend integration guide |
| [SETUP.md](SETUP.md) | Detailed frontend setup steps |

---

**Version:** 2.0 — React 18 + TypeScript + Vite · WebSocket · Web Speech API · Client IP pipeline
