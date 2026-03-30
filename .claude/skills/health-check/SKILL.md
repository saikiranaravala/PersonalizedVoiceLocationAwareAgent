---
name: health-check
description: Check that the backend is healthy, WebSocket is reachable, and all required API keys are configured. Use when the user reports connection issues or wants to verify the stack is running.
disable-model-invocation: true
allowed-tools: Bash, Read
---

# Health Check

Verify the full stack is operational.

## Steps

### 1. Check required environment variables

```bash
echo "=== API Key Status ==="
grep -q "OPENROUTER_API_KEY" config/.env 2>/dev/null && echo "✓ OPENROUTER_API_KEY" || echo "✗ OPENROUTER_API_KEY missing"
grep -q "TICKETMASTER_API_KEY" config/.env 2>/dev/null && echo "✓ TICKETMASTER_API_KEY" || echo "✗ TICKETMASTER_API_KEY missing (Events tool disabled)"
grep -q "LANGCHAIN_TRACING_V2=true" config/.env 2>/dev/null && echo "✓ LangSmith tracing enabled" || echo "  LangSmith tracing off"
```

### 2. Backend REST health endpoint

```bash
echo "=== Backend Health ==="
curl -s http://localhost:8000/health | python -m json.tool 2>/dev/null || echo "✗ Backend not reachable on :8000"
```

### 3. Backend context endpoint

```bash
echo "=== Conversation Context ==="
curl -s http://localhost:8000/context | python -m json.tool 2>/dev/null || echo "✗ /context not responding"
```

### 4. Frontend dev server

```bash
echo "=== Frontend ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 | grep -q "200" && echo "✓ Vite dev server on :5173" || echo "✗ Frontend not running on :5173"
```

### 5. External service reachability

```bash
echo "=== External Services ==="
curl -s "https://api.ipify.org?format=json" | python -m json.tool && echo "✓ ipify.org reachable" || echo "✗ ipify.org unreachable"
curl -s -o /dev/null -w "%{http_code}" "https://nominatim.openstreetmap.org/status" | grep -q "200" && echo "✓ Nominatim reachable" || echo "✗ Nominatim unreachable"
curl -s -o /dev/null -w "%{http_code}" "https://overpass-api.de/api/status" | grep -q "200" && echo "✓ Overpass API reachable" || echo "✗ Overpass API unreachable"
curl -s -o /dev/null -w "%{http_code}" "https://api.open-meteo.com/v1/forecast?latitude=0&longitude=0&current_weather=true" | grep -q "200" && echo "✓ Open-Meteo reachable" || echo "✗ Open-Meteo unreachable"
```

### 6. Python dependencies

```bash
echo "=== Python Deps ==="
python -c "import fastapi, langchain, loguru; print('✓ Core backend packages OK')" 2>&1
python -c "import geocoder, geopy; print('✓ Location packages OK')" 2>&1
```

### 7. Node dependencies

```bash
echo "=== Node Deps ==="
[ -d ui/node_modules ] && echo "✓ node_modules present" || echo "✗ Run: cd ui && npm install"
```

## Interpret results

| Symbol | Meaning |
| ------ | ------- |
| ✓ | OK |
| ✗ | Problem — report the specific failure to the user with the fix |
|   | Optional / informational |

After running all checks, summarise what is healthy and what needs attention. If any ✗ appears, provide the exact command to fix it.
