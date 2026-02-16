# Troubleshooting Guide - OpenRouter Integration

## Common Errors and Fixes

### Error 1: "functions" and "function_call" are deprecated

**Full Error:**
```
Error code: 400 - {'error': {'message': '"functions" and "function_call" are deprecated 
in favor of "tools" and "tool_choice."', 'code': 400}}
```

**Cause:** Using old LangChain agent type with OpenRouter

**Fix Applied:** ✅ Updated to use `create_tool_calling_agent` instead of `create_openai_functions_agent`

**What Changed:**
- File: `src/agent/core.py`
- Old: `create_openai_functions_agent()`
- New: `create_tool_calling_agent()`

**Verify Fix:**
```bash
# Check the imports in src/agent/core.py
grep "create_tool_calling_agent" src/agent/core.py
# Should show: from langchain.agents import AgentExecutor, create_tool_calling_agent
```

---

### Error 2: Model doesn't support tool calling

**Error:**
```
Tool calling not supported for this model
```

**Cause:** Some models on OpenRouter don't support function/tool calling

**Solutions:**

**Option 1: Use a model with tool calling support (Recommended)**
```yaml
# config/config.yaml
agent:
  model: "anthropic/claude-3-sonnet"  # ✅ Full tool support
  # OR
  model: "anthropic/claude-3-opus"    # ✅ Full tool support
  # OR
  model: "openai/gpt-4-turbo"         # ✅ Full tool support
```

**Option 2: Check model capabilities**
Visit https://openrouter.ai/models and look for "Function Calling" badge

**Models with GOOD tool calling support:**
- ✅ `anthropic/claude-3-opus`
- ✅ `anthropic/claude-3-sonnet`
- ✅ `anthropic/claude-3-haiku`
- ✅ `openai/gpt-4-turbo`
- ✅ `openai/gpt-4`
- ✅ `openai/gpt-3.5-turbo`

**Models with LIMITED/NO tool calling:**
- ⚠️ `meta-llama/llama-3-70b-instruct` (limited)
- ❌ `mistralai/mistral-7b-instruct` (no support)
- ❌ Older models generally don't support it

---

### Error 3: OPENROUTER_API_KEY not found

**Error:**
```
ERROR: OPENROUTER_API_KEY not found in environment
```

**Fix:**

1. **Create/Edit config/.env file:**
```bash
# Windows
notepad config\.env
```

2. **Add your API key:**
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

3. **Get your key from:**
https://openrouter.ai/keys

4. **Verify the key format:**
- Should start with: `sk-or-v1-`
- No quotes needed
- No extra spaces

---

### Error 4: Invalid API key

**Error:**
```
Error: Invalid authentication
```

**Fixes:**

1. **Check key format:**
```bash
# In config/.env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx  # ✅ Correct
OPENROUTER_API_KEY="sk-or-v1-xxx"        # ❌ Remove quotes
OPENROUTER_API_KEY= sk-or-v1-xxx         # ❌ Remove space
```

2. **Verify key is active:**
- Visit https://openrouter.ai/keys
- Check if key is enabled
- Check if you have credits

3. **Test key directly:**
```bash
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_KEY_HERE"
```

---

### Error 5: Insufficient credits

**Error:**
```
Error: Insufficient credits
```

**Fix:**
1. Go to https://openrouter.ai/credits
2. Add credits to your account
3. Minimum: $5 recommended for testing

**Check current balance:**
```bash
curl https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer YOUR_KEY_HERE"
```

---

### Error 6: Model not found

**Error:**
```
Error: Model 'xxx' not found
```

**Cause:** Incorrect model name format

**Fix - Use exact model identifiers:**
```yaml
# ✅ CORRECT formats:
model: "anthropic/claude-3-sonnet"
model: "openai/gpt-4-turbo"
model: "meta-llama/llama-3-70b-instruct"

# ❌ WRONG formats:
model: "claude-3-sonnet"           # Missing provider
model: "gpt-4"                     # Wrong for OpenRouter
model: "anthropic/claude-3"        # Incomplete
```

**Find correct names:**
https://openrouter.ai/models

---

### Error 7: Rate limit exceeded

**Error:**
```
Error: Rate limit exceeded
```

**Temporary Fix:**
Wait 60 seconds and try again

**Permanent Fix:**
```yaml
# config/config.yaml
agent:
  retry_attempts: 5       # Increase retries
  timeout_seconds: 60     # Increase timeout
```

**Check limits:**
https://openrouter.ai/docs/limits

---

### Error 8: Connection timeout

**Error:**
```
Error: Connection timeout
```

**Fixes:**

1. **Check internet connection**

2. **Increase timeout:**
```yaml
# config/config.yaml
agent:
  timeout_seconds: 60  # Increase from default 30
```

3. **Check OpenRouter status:**
https://status.openrouter.ai

---

### Error 9: Model response parsing error

**Error:**
```
Error: Could not parse model output
```

**Fix:**
```yaml
# config/config.yaml
agent:
  # Enable parsing error handling
  handle_parsing_errors: true  # Already enabled by default
```

**Alternative:**
Try a different model with better structured output:
```yaml
model: "anthropic/claude-3-sonnet"  # More consistent outputs
```

---

### Error 10: Tool execution failed

**Error:**
```
Error in get_weather: [some error]
```

**Debug steps:**

1. **Check logs:**
```bash
cat logs/agent.log | grep ERROR
```

2. **Test tool directly:**
```python
# In Python console
from services.location import LocationService
from tools.weather import WeatherTool

loc = LocationService()
weather = WeatherTool(loc)
result = weather.execute()
print(result)
```

3. **Check API access:**
- Weather API (open-meteo) needs internet
- Zomato needs API key (or uses mock data)

---

## Verification Steps

### Step 1: Verify Installation
```bash
# Check if all packages installed
pip list | grep langchain
pip list | grep openai
```

Should show:
- langchain==0.2.0 (or higher)
- langchain-openai==0.1.7 (or higher)
- openai==1.30.1 (or higher)

### Step 2: Verify Configuration
```bash
# Check config file
cat config/config.yaml | grep use_openrouter
# Should show: use_openrouter: true

# Check env file
cat config/.env | grep OPENROUTER
# Should show: OPENROUTER_API_KEY=sk-or-v1-...
```

### Step 3: Verify Model Support
```bash
# Test API connection
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_KEY" | jq '.data[] | select(.id=="anthropic/claude-3-sonnet")'
```

### Step 4: Test with Minimal Query
```python
# src/test_openrouter.py
from agent.core import AgenticAssistant

assistant = AgenticAssistant()
response = assistant.process_request("Hello")
print(response)
```

---

## Quick Diagnostic Script

Save as `diagnose.py` in project root:

```python
#!/usr/bin/env python3
"""Quick diagnostic for OpenRouter setup."""

import os
import sys
from pathlib import Path

print("🔍 OpenRouter Diagnostic\n")

# Check 1: Environment file
env_file = Path("config/.env")
if env_file.exists():
    print("✅ config/.env exists")
    with open(env_file) as f:
        content = f.read()
        if "OPENROUTER_API_KEY" in content:
            print("✅ OPENROUTER_API_KEY found in .env")
        else:
            print("❌ OPENROUTER_API_KEY not found in .env")
else:
    print("❌ config/.env not found")

# Check 2: Config file
config_file = Path("config/config.yaml")
if config_file.exists():
    print("✅ config/config.yaml exists")
    with open(config_file) as f:
        content = f.read()
        if "use_openrouter: true" in content:
            print("✅ use_openrouter is enabled")
        else:
            print("⚠️  use_openrouter is disabled (using OpenAI)")
else:
    print("❌ config/config.yaml not found")

# Check 3: Required packages
try:
    import langchain
    print(f"✅ langchain installed ({langchain.__version__})")
except ImportError:
    print("❌ langchain not installed")

try:
    from langchain_openai import ChatOpenAI
    print("✅ langchain-openai installed")
except ImportError:
    print("❌ langchain-openai not installed")

# Check 4: API Key in environment
if os.getenv("OPENROUTER_API_KEY"):
    key = os.getenv("OPENROUTER_API_KEY")
    if key.startswith("sk-or-v1-"):
        print("✅ OPENROUTER_API_KEY loaded (correct format)")
    else:
        print("⚠️  OPENROUTER_API_KEY loaded but wrong format")
else:
    print("❌ OPENROUTER_API_KEY not in environment")

print("\n📋 Summary:")
print("If all checks passed, OpenRouter should work!")
print("If any failed, check the error messages above.")
```

Run with:
```bash
python diagnose.py
```

---

## Getting Help

### Documentation
- **OpenRouter Guide**: See `OPENROUTER_GUIDE.md`
- **Quick Reference**: See `OPENROUTER_QUICK_REF.md`
- **Changes Log**: See `OPENROUTER_CHANGES.md`

### External Resources
- **OpenRouter Docs**: https://openrouter.ai/docs
- **Discord**: https://discord.gg/openrouter
- **Status Page**: https://status.openrouter.ai
- **Model List**: https://openrouter.ai/models

### Debug Mode
Run with verbose logging:
```bash
python src/main.py --debug
```

Check logs:
```bash
cat logs/agent.log
```

---

## Best Practices to Avoid Issues

1. **Use recommended models** (Claude 3 Sonnet, GPT-4 Turbo)
2. **Check credits** before heavy usage
3. **Monitor usage** at https://openrouter.ai/activity
4. **Set budget limits** in OpenRouter dashboard
5. **Test with simple queries** first
6. **Keep API key secure** (never commit to git)
7. **Update packages** regularly: `pip install -r requirements.txt --upgrade`

---

## Still Having Issues?

1. **Check this file first** for your specific error
2. **Run diagnostic script**: `python diagnose.py`
3. **Check logs**: `cat logs/agent.log`
4. **Try OpenAI mode** as fallback: Set `use_openrouter: false`
5. **Test API key** directly with curl commands above
6. **Visit OpenRouter status**: https://status.openrouter.ai

**Most issues are configuration problems, not code bugs!**
