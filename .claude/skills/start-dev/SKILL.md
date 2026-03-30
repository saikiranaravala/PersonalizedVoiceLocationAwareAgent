---
name: start-dev
description: Start the backend (FastAPI) and frontend (Vite) dev servers. Use when the user wants to run the project locally.
argument-hint: [backend-only | frontend-only]
disable-model-invocation: true
allowed-tools: Bash
---

# Start Development Servers

Start the voice assistant dev environment. Default starts both backend and frontend.

## Argument

`$ARGUMENTS` may be `backend-only`, `frontend-only`, or empty (start both).

## Steps

1. **Check environment** — confirm `config/.env` exists and has required keys:

```bash
if [ ! -f config/.env ]; then
  echo "⚠ config/.env not found — copy config/.env.example and add API keys"
fi
grep -q "OPENROUTER_API_KEY" config/.env 2>/dev/null && echo "✓ OPENROUTER_API_KEY set" || echo "⚠ OPENROUTER_API_KEY missing"
grep -q "TICKETMASTER_API_KEY" config/.env 2>/dev/null && echo "✓ TICKETMASTER_API_KEY set" || echo "⚠ TICKETMASTER_API_KEY missing"
```

2. **Start backend** (skip if `frontend-only`):

```bash
python api_server.py
```

Backend starts on `http://localhost:8000`. Verify with:

```bash
curl http://localhost:8000/health
```

3. **Start frontend** (skip if `backend-only`):

```bash
cd ui && npm run dev
```

Frontend starts on `http://localhost:5173`.

## Expected output

- Backend: `✓ Assistant initialized successfully` then `Uvicorn running on http://0.0.0.0:8000`
- Frontend: `➜ Local: http://localhost:5173/`

## Troubleshooting

- **Port 8000 in use**: `lsof -i :8000` to find the process
- **Module not found**: `pip install -r requirements.txt`
- **npm ERR**: `cd ui && npm install` first
- **WebSocket not connecting**: ensure `VITE_WS_URL` is unset (dev) or set to `ws://localhost:8000`
