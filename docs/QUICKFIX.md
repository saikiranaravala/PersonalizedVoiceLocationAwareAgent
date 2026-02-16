# Quick Fix Guide - Error 400 "functions deprecated"

## The Problem

You're getting this error:
```
Error code: 400 - {'error': {'message': '"functions" and "function_call" are deprecated 
in favor of "tools" and "tool_choice."'}}
```

## The Fix (3 Steps)

### Step 1: Update the Code ✅ (Already Done)

The code has been updated to use the new `create_tool_calling_agent` instead of the deprecated `create_openai_functions_agent`.

**Verify the fix is applied:**

Open `src/agent/core.py` and check line 6:
```python
from langchain.agents import AgentExecutor, create_tool_calling_agent  # ✅ Should see this
```

NOT:
```python
from langchain.agents import AgentExecutor, create_openai_functions_agent  # ❌ Old version
```

### Step 2: Update Dependencies

Make sure you have the latest LangChain version:

```bash
pip install --upgrade langchain langchain-openai langchain-core
```

Or reinstall from requirements:
```bash
pip install -r requirements.txt --upgrade
```

### Step 3: Restart the Application

```bash
python src/main.py
```

## Verify It's Fixed

You should see:
```
✓ Using OpenRouter API
Initializing Agentic Assistant...
Initialized LLM via OpenRouter: anthropic/claude-3-sonnet
...
```

Instead of the error.

## Still Getting the Error?

### Option 1: Run Diagnostic

```bash
python diagnose.py
```

This will check your configuration and show any issues.

### Option 2: Check Your Model

Some models might have issues. Use one of these tested models:

```yaml
# config/config.yaml
agent:
  use_openrouter: true
  model: "anthropic/claude-3-sonnet"  # ✅ RECOMMENDED
  # OR
  model: "openai/gpt-4-turbo"         # ✅ Also works
  # OR  
  model: "anthropic/claude-3-haiku"   # ✅ Fast & cheap
```

### Option 3: Verify Configuration

**Check config/.env:**
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key  # Should start with sk-or-v1-
```

**Check config/config.yaml:**
```yaml
agent:
  use_openrouter: true                      # Should be true
  model: "anthropic/claude-3-sonnet"        # Use full format with provider
```

### Option 4: Fallback to OpenAI

If OpenRouter isn't working, you can temporarily switch back:

**config/config.yaml:**
```yaml
agent:
  use_openrouter: false  # Switch to OpenAI
  model: "gpt-4"
```

**config/.env:**
```bash
OPENAI_API_KEY=sk-your-openai-key  # Make sure this is set
```

## What Changed?

| Before | After |
|--------|-------|
| `create_openai_functions_agent()` | `create_tool_calling_agent()` |
| Uses deprecated "functions" API | Uses modern "tools" API |
| ❌ Fails with OpenRouter | ✅ Works with OpenRouter |

## Technical Details

The old LangChain agent used the "functions" format for tool calling:
```json
{
  "functions": [...],
  "function_call": {...}
}
```

The new agent uses the "tools" format:
```json
{
  "tools": [...],
  "tool_choice": {...}
}
```

OpenRouter requires the new format, which is why the old code failed.

## Need More Help?

1. **Run diagnostic**: `python diagnose.py`
2. **Check logs**: `cat logs/agent.log`
3. **Read troubleshooting**: See `TROUBLESHOOTING.md`
4. **Test simple query**: Try just "hello" first

## Summary

✅ **The fix is already applied**
✅ **Just update your dependencies and restart**
✅ **Use a recommended model (Claude 3 Sonnet)**

The error should be gone! 🎉
