---
name: debug-location
description: Diagnose location resolution issues — wrong city in results, geocoding failures, Nominatim 429 errors, or client IP pipeline problems. Use when tool results show the wrong location.
disable-model-invocation: true
allowed-tools: Read, Grep, Bash
---

# Debug Location Resolution

Diagnose why the assistant is returning results for the wrong city, or why geocoding is failing.

## The correct priority chain

```
1. Profile lat/lon  → use directly            ← highest priority
2. Profile city/state → Nominatim geocode
3. client_ip (browser via ipify.org)  → ipinfo.io
4. Config fallback_location            ← last resort only
```

Server IP (`geocoder.ip('me')`) must never be reached. If it is, the pipeline is broken.

## Step 1 — Check what IP the backend is seeing

Search recent backend output or logs:

```bash
grep -r "Client IP" . --include="*.log" -i 2>/dev/null | tail -20
grep -r "client_ip" src/ --include="*.py" -l
```

The log line should show the user's real public IP (e.g. `24.x.x.x`), **not** a private IP (`10.x.x.x`, `172.x.x.x`, `127.x.x.x`) or the server host IP.

If a private IP appears → the `X-Forwarded-For` header is not being set. Check:
- Render: automatic ✓
- Nginx: needs `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;`
- Direct uvicorn: not behind a proxy — client IP comes from socket directly

## Step 2 — Check that client.ts sends `client_ip`

```bash
grep -n "client_ip" ui/src/api/client.ts
grep -n "ipify" ui/src/hooks/useVoiceAssistant.ts
```

Both should exist. If `client_ip` is missing from `client.ts` Message interface or payload, the field never reaches the backend.

## Step 3 — Check `api_server.py` extracts the IP correctly

```bash
grep -n -A 5 "x-forwarded-for\|x-real-ip\|client_ip" api_server.py
```

Expected pattern:
```python
client_ip = (
    websocket.headers.get("x-forwarded-for", "").split(",")[0].strip()
    or websocket.headers.get("x-real-ip", "")
    or (websocket.client.host if websocket.client else None)
) or None
```

## Step 4 — Check `core.py` geocodes the profile before any tool runs

```bash
grep -n "_extract_location_from_profile\|Geocoded user profile\|sleep(1.1)" src/agent/core.py
```

The log line `Geocoded user profile location 'Erie, PENNSYLVANIA' → (42.1292, -80.0851)` must appear **before** any tool call in the logs.

## Step 5 — Check for Nominatim 429 errors

```bash
grep -r "429\|rate.limit\|Retry\|backoff" src/tools/restaurant_finder.py
grep -r "429\|rate.limit" . --include="*.log" -i 2>/dev/null | tail -10
```

The retry logic must be present in `restaurant_finder.py`:
- Pre-sleep: `time.sleep(1.1 * (attempt + 1))`
- 429 backoff: `time.sleep(2 ** (attempt + 1))`

If 429s are persistent: increase `time.sleep` multiplier or reduce call frequency.

## Step 6 — Check LocationContextAdapter priority

```bash
grep -n "get_current_location\|_client_ip\|profile.*lat\|geocode_query" src/agent/core.py
```

`location_adapter._client_ip` and `location_service._client_ip` must both be set from `client_ip` before tools are invoked.

## Step 7 — Quick end-to-end location test

Send a direct HTTP POST to the backend:

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What city am I in?", "user_profile": {"city": "Erie", "state": "PENNSYLVANIA"}, "client_ip": "24.210.110.237"}' \
  | python -m json.tool
```

The response should mention Erie, PA — not any other city.

## Common fixes

| Symptom | Root cause | Fix |
| ------- | ---------- | --- |
| Columbus, OH results | Server IP used | Ensure `client_ip` flows through all layers |
| Profile city ignored | `_extract_location_from_profile` not called | Check `core.py` calls it before `agent_executor.invoke` |
| Nominatim returning wrong city | Geocode query format | Confirm query is `"City, STATE"` not just city name |
| 429 on every request | Pre-sleep missing | Add `time.sleep(1.1)` before each Nominatim call |
| `latitude`/`longitude` key error | Old `lat`/`lon` key names | All references must use `latitude`/`longitude` |
