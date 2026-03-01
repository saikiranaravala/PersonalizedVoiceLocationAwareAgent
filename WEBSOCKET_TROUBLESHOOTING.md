# WebSocket Connection Troubleshooting Guide

## Issue: Frontend Not Connecting to Backend

If you see "Not connected to backend" message in the UI, follow these steps:

### 1. Verify Backend is Running

**Check if backend server is running:**

```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

**Expected output:** Should show a process listening on port 8000

**If not running, start it:**
```bash
python api_server.py
```

**Expected console output:**
```
🚀 Personalized Agentic Assistant API Server
✓ Assistant initialized successfully
INFO:     Started server process [XXXX]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### 2. Test Backend Health

**Open browser and navigate to:**
```
http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "agentic-assistant",
  "assistant_initialized": true
}
```

**If you see an error:**
- Backend may not be running
- Port 8000 is blocked by firewall
- Another service is using port 8000

---

### 3. Test WebSocket Connection Manually

**Option A: Using Browser Console**

Open browser console (F12) on the frontend page and run:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/test123');

ws.onopen = () => {
    console.log('✓ WebSocket connected!');
    ws.send(JSON.stringify({
        type: 'chat',
        message: 'Hello'
    }));
};

ws.onmessage = (event) => {
    console.log('Received:', JSON.parse(event.data));
};

ws.onerror = (error) => {
    console.error('✗ WebSocket error:', error);
};

ws.onclose = () => {
    console.log('WebSocket closed');
};
```

**Expected output:**
```
✓ WebSocket connected!
Received: {type: "status", status: "processing", message: "Processing..."}
Received: {type: "response", message: "...", success: true}
```

**Option B: Using curl (for testing REST API)**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What's the weather?\"}"
```

---

### 4. Check Browser Console for Errors

**Open browser developer tools (F12) and check for:**

❌ **WebSocket connection failed**
```
WebSocket connection to 'ws://localhost:8000/ws/...' failed
```
**Solution:** Backend not running or wrong URL

❌ **CORS error**
```
Access to fetch at 'http://localhost:8000/chat' from origin 'http://localhost:5173'
has been blocked by CORS policy
```
**Solution:** Backend CORS settings need update (should already be configured)

❌ **Network error**
```
Failed to fetch
```
**Solution:** Backend not accessible - check if it's running

---

### 5. Verify Frontend Configuration

**Check that the WebSocket URL is correct in the frontend:**

The hook should be connecting to:
```typescript
backendUrl: 'ws://localhost:8000'
```

**If backend is on different host/port, update App.tsx:**
```typescript
const {
  // ...
} = useVoiceAssistant({
  backendUrl: 'ws://YOUR_HOST:YOUR_PORT',  // Update this
  // ...
});
```

---

### 6. Common Issues & Solutions

#### Issue: "Connection refused"
**Cause:** Backend not running
**Solution:** Start backend with `python api_server.py`

#### Issue: "Port 8000 already in use"
**Cause:** Another process using port 8000
**Solution:**
```bash
# Windows - find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in api_server.py:
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use 8001
# Then update frontend to ws://localhost:8001
```

#### Issue: Backend starts but crashes immediately
**Cause:** Missing dependencies or API key
**Solution:**
```bash
# Install dependencies
pip install -r requirements.txt --break-system-packages

# Check API key is set
cat config/.env  # Should show OPENAI_API_KEY or OPENROUTER_API_KEY
```

#### Issue: "Assistant not initialized"
**Cause:** Invalid API key or missing configuration
**Solution:**
1. Check `config/.env` has valid API key
2. Check `config/config.yaml` has correct model settings
3. Restart backend after fixing

#### Issue: WebSocket connects but no response
**Cause:** Backend error processing request
**Solution:**
1. Check backend console for error messages
2. Verify tools are configured correctly
3. Check API key has sufficient credits

#### Issue: Speech recognition not working
**Cause:** Browser doesn't support Web Speech API
**Solution:**
- Use Chrome/Edge (best support)
- Firefox has limited support
- Safari on iOS works well
- Allow microphone permissions when prompted

---

### 7. Testing Speech Recognition

**Verify microphone access:**

1. Click voice button
2. Browser should prompt for microphone permission
3. Allow access
4. Speak clearly into microphone
5. You should see "Listening..." status

**If microphone not working:**
- Check browser permissions (usually shows icon in address bar)
- Try different browser (Chrome recommended)
- Check system microphone settings
- Verify microphone is not muted

**Check in browser console:**
```javascript
// Test if speech recognition is available
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    console.log('✓ Speech Recognition supported');
} else {
    console.log('✗ Speech Recognition NOT supported');
}
```

---

### 8. Network Debugging

**If issues persist, check network tab in browser DevTools:**

1. Open DevTools (F12)
2. Go to Network tab
3. Click voice button
4. Look for WebSocket connection (WS tab)

**Healthy connection shows:**
- Status: 101 Switching Protocols
- Green dot indicating active connection
- Messages flowing back and forth

**Failed connection shows:**
- Status: 4xx or 5xx error
- Red indicator
- No messages

---

### 9. Backend Logs

**Check backend console output for:**

✅ **Successful connection:**
```
[Voice Assistant] Initializing WebSocket...
✓ Client session_123... connected via WebSocket
Received message type: chat from session_123...
```

❌ **Failed connection:**
```
WebSocket error for session_123: Connection closed
ERROR: Failed to process message: [error details]
```

**Enable verbose logging by setting in api_server.py:**
```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    log_level="debug"  # Change from "info" to "debug"
)
```

---

### 10. Quick Diagnostic Checklist

Run through this checklist:

- [ ] Backend server running (`python api_server.py`)
- [ ] Backend health check passes (`http://localhost:8000/health`)
- [ ] Frontend running (`cd ui && npm run dev`)
- [ ] Frontend accessible (`http://localhost:5173`)
- [ ] No errors in frontend browser console (F12)
- [ ] No errors in backend terminal
- [ ] API key configured in `config/.env`
- [ ] Microphone permission granted in browser
- [ ] Using Chrome/Edge browser (best support)
- [ ] No firewall blocking ports 8000 or 5173

---

### 11. Test Flow

**Complete end-to-end test:**

1. **Start backend:**
   ```bash
   python api_server.py
   ```
   → Should see "Assistant initialized successfully"

2. **Start frontend:**
   ```bash
   cd ui
   npm run dev
   ```
   → Opens browser to localhost:5173

3. **Verify connection:**
   - Look for green dot next to "Voice Assistant" title
   - No red warning banner at top

4. **Test quick action:**
   - Click "Weather" button
   - Should see conversation bubble appear
   - Backend logs should show message received

5. **Test voice:**
   - Click microphone button
   - Allow microphone access if prompted
   - Speak "What's the weather?"
   - Should see "Listening..." → "Processing..." → "Speaking..."
   - Response appears in conversation

---

### 12. Still Not Working?

**Collect debug information:**

1. **Backend logs:**
   ```bash
   python api_server.py > backend.log 2>&1
   ```
   Save the output

2. **Frontend console:**
   - F12 → Console tab
   - Take screenshot of any errors

3. **Network tab:**
   - F12 → Network tab → WS
   - Take screenshot of WebSocket connection status

4. **Configuration:**
   ```bash
   # Backend config
   cat config/.env
   cat config/config.yaml
   
   # Frontend config
   cat ui/src/hooks/useVoiceAssistant.ts | grep backendUrl
   ```

**Share this information when asking for help!**

---

## Success Indicators

When everything is working correctly, you should see:

**Backend Terminal:**
```
🚀 Personalized Agentic Assistant API Server
✓ Assistant initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
✓ Client session_xxx connected via WebSocket
Received message type: chat from session_xxx
```

**Frontend UI:**
- Green dot next to "Voice Assistant" title
- No warning banners
- Voice button enabled (not grayed out)
- Quick action buttons enabled

**Browser Console:**
```
[WebSocket] Connecting to ws://localhost:8000/ws/session_xxx...
[WebSocket] Connected successfully
[Voice Assistant] Connected to backend
[Voice Recognition] Started listening
[WebSocket] Sending: {type: "chat", message: "..."}
[WebSocket] Received: {type: "status", status: "processing"}
[WebSocket] Received: {type: "response", message: "..."}
```

---

## Quick Fix Commands

```bash
# Restart everything fresh
cd personalized-agentic-assistant

# Kill any existing processes
# Windows:
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Start backend
python api_server.py

# In new terminal, start frontend
cd ui
npm run dev

# If dependencies missing
pip install -r requirements.txt --break-system-packages
cd ui && npm install

# If port conflicts
# Change port in api_server.py: uvicorn.run(app, port=8001)
# Update frontend: backendUrl: 'ws://localhost:8001'
```

---

**Need more help?** Check the main documentation files:
- `FULLSTACK_SETUP.md` - Complete setup guide
- `ui/README.md` - Frontend documentation
- `TROUBLESHOOTING.md` - General troubleshooting
