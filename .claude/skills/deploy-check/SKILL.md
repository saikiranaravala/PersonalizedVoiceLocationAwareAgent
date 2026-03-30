---
name: deploy-check
description: Run a pre-deployment checklist before pushing to Render (or any cloud). Verifies env vars, build, CORS, WebSocket URL, and security settings. Use before deploying.
argument-hint: [render | nginx | docker]
disable-model-invocation: true
allowed-tools: Read, Grep, Bash
---

# Pre-Deployment Checklist

Verify the project is ready for production deployment.

## Argument

`$ARGUMENTS` — deployment target: `render` (default), `nginx`, or `docker`.

## Step 1 — Frontend production build

```bash
cd ui && npm run build 2>&1 | tail -30
```

Must complete with no TypeScript errors. The `dist/` directory must be created.

Also verify `_redirects` exists for SPA routing:

```bash
cat ui/_redirects
```

Expected: `/* /index.html 200`

## Step 2 — Environment variable checklist

```bash
echo "=== Backend .env ==="
grep -q "OPENROUTER_API_KEY" config/.env && echo "✓ OPENROUTER_API_KEY" || echo "✗ MISSING — LLM will not work"
grep -q "TICKETMASTER_API_KEY" config/.env && echo "✓ TICKETMASTER_API_KEY" || echo "⚠ MISSING — Events tool disabled"
echo ""
echo "=== Frontend .env ==="
grep -q "VITE_WS_URL=wss://" ui/.env 2>/dev/null && echo "✓ VITE_WS_URL uses wss://" || echo "✗ VITE_WS_URL must be wss:// for HTTPS deployment"
grep -q "VITE_API_URL=https://" ui/.env 2>/dev/null && echo "✓ VITE_API_URL uses https://" || echo "⚠ VITE_API_URL should use https://"
```

**Critical:** `VITE_WS_URL` **must** use `wss://` (not `ws://`) when the frontend is served over HTTPS. Browsers block mixed content.

## Step 3 — Security checks

```bash
echo "=== Security ==="
# .env must not be committed
git ls-files config/.env 2>/dev/null && echo "✗ config/.env is tracked by git — remove it!" || echo "✓ config/.env not committed"
git ls-files ui/.env 2>/dev/null && echo "✗ ui/.env is tracked by git — remove it!" || echo "✓ ui/.env not committed"

# .gitignore must cover .env files
grep -q "\.env" .gitignore 2>/dev/null && echo "✓ .env in .gitignore" || echo "⚠ Add .env to .gitignore"

# TICKETMASTER key must not be in frontend bundle
grep -r "TICKETMASTER" ui/src/ 2>/dev/null && echo "✗ TICKETMASTER key referenced in frontend!" || echo "✓ TICKETMASTER key not in frontend"
```

## Step 4 — CORS configuration

```bash
echo "=== CORS ==="
grep -n "allow_origins\|CORSMiddleware" api_server.py
```

For production, `allow_origins` must **not** be `["*"]`. It should list only the known frontend domain(s).

## Step 5 — Render-specific checks (if target is `render`)

Verify `api_server.py` reads the port from the environment (Render injects `PORT`):

```bash
grep -n "PORT\|port\|uvicorn.run\|0\.0\.0\.0" api_server.py
```

Expected: `host="0.0.0.0"` and `port=int(os.getenv("PORT", 8000))`.

Verify the `X-Forwarded-For` extraction is present (Render's LB sets this):

```bash
grep -n "x-forwarded-for\|X-Forwarded-For" api_server.py
```

## Step 6 — Nginx-specific checks (if target is `nginx`)

Confirm the Nginx config includes WebSocket upgrade headers:

```bash
grep -n "Upgrade\|Connection.*upgrade\|X-Forwarded-For\|X-Real-IP" /etc/nginx/sites-enabled/* 2>/dev/null || echo "Check your nginx config manually"
```

## Step 7 — TypeScript strict check

```bash
cd ui && npm run type-check
```

No errors must appear. Warnings are acceptable but worth reviewing.

## Step 8 — Final summary

After running all steps, output a table:

| Check | Status | Action needed |
| ----- | ------ | ------------- |
| Frontend builds | ✓/✗ | ... |
| `_redirects` present | ✓/✗ | ... |
| Backend API keys | ✓/✗ | ... |
| `VITE_WS_URL` uses wss:// | ✓/✗ | ... |
| `.env` not committed | ✓/✗ | ... |
| CORS restricted | ✓/✗ | ... |
| Render PORT handling | ✓/✗ | ... |
| TypeScript clean | ✓/✗ | ... |

Only deploy if all critical items (✗ blockers) are resolved.
