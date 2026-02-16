# OpenRouter Integration Guide

## What is OpenRouter?

OpenRouter is a unified API that provides access to multiple LLM providers (OpenAI, Anthropic, Meta, Google, etc.) through a single interface. It offers:

- **Multi-provider access**: Use Claude, GPT-4, Llama, and more
- **Cost optimization**: Automatic fallbacks and routing
- **Unified billing**: Single API key for all models
- **Transparent pricing**: Pay only for what you use

Website: https://openrouter.ai

## Setup Instructions

### 1. Get Your OpenRouter API Key

1. Go to https://openrouter.ai
2. Sign up or log in
3. Navigate to https://openrouter.ai/keys
4. Click "Create Key"
5. Copy your API key (starts with `sk-or-v1-...`)

### 2. Configure the Application

**Option A: Use config/.env file (Recommended)**

```bash
# Edit config/.env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Option B: Use environment variable**

```bash
# Windows Command Prompt
set OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Windows PowerShell
$env:OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

### 3. Enable OpenRouter in Configuration

Edit `config/config.yaml`:

```yaml
agent:
  use_openrouter: true  # Changed from false to true
  model: "anthropic/claude-3-sonnet"  # Choose your model
  temperature: 0.7
```

### 4. Run the Application

```bash
python src/main.py
```

You should see: `✓ Using OpenRouter API`

## Available Models

### Popular Models on OpenRouter

| Model | Identifier | Best For | Cost (per 1M tokens) |
|-------|-----------|----------|---------------------|
| **Claude 3 Opus** | `anthropic/claude-3-opus` | Complex reasoning, function calling | $15 / $75 |
| **Claude 3 Sonnet** | `anthropic/claude-3-sonnet` | Balanced performance | $3 / $15 |
| **Claude 3.5 Sonnet** | `anthropic/claude-3.5-sonnet` | Latest Claude model | $3 / $15 |
| **Claude 3 Haiku** | `anthropic/claude-3-haiku` | Fast, cost-effective | $0.25 / $1.25 |
| **GPT-4 Turbo** | `openai/gpt-4-turbo` | OpenAI's latest GPT-4 | $10 / $30 |
| **GPT-4** | `openai/gpt-4` | Best OpenAI reasoning | $30 / $60 |
| **GPT-3.5 Turbo** | `openai/gpt-3.5-turbo` | Fast, cheap | $0.50 / $1.50 |
| **Llama 3 70B** | `meta-llama/llama-3-70b-instruct` | Open-source, free | $0.59 / $0.79 |
| **Mixtral 8x7B** | `mistralai/mixtral-8x7b-instruct` | Open-source MoE | $0.24 / $0.24 |
| **Gemini Pro** | `google/gemini-pro` | Google's model | $0.50 / $1.50 |

*Prices shown as: Input / Output per 1M tokens*

Full model list: https://openrouter.ai/models

## Configuration Examples

### Example 1: Use Claude 3 Sonnet (Recommended for this project)

```yaml
# config/config.yaml
agent:
  use_openrouter: true
  model: "anthropic/claude-3-sonnet"
  temperature: 0.7
```

**Why?** Claude excels at tool use and function calling, which is core to this assistant.

### Example 2: Use GPT-4 via OpenRouter

```yaml
# config/config.yaml
agent:
  use_openrouter: true
  model: "openai/gpt-4-turbo"
  temperature: 0.7
```

**Why?** GPT-4 has excellent reasoning and is familiar to most users.

### Example 3: Use Free/Cheap Model (Llama 3)

```yaml
# config/config.yaml
agent:
  use_openrouter: true
  model: "meta-llama/llama-3-70b-instruct"
  temperature: 0.7
```

**Why?** Great for testing without spending money. Performance is good for most tasks.

### Example 4: Use Direct OpenAI (Original Setup)

```yaml
# config/config.yaml
agent:
  use_openrouter: false
  model: "gpt-4"
  temperature: 0.7
```

**Why?** You prefer using OpenAI directly instead of through OpenRouter.

## Code Changes Summary

The following files were modified to support OpenRouter:

### 1. `src/agent/core.py`
- Added `create_openrouter_llm()` function
- Modified `_initialize_llm()` to check `use_openrouter` config
- Automatically adds required headers for OpenRouter

### 2. `src/utils/config.py`
- Added `openrouter_api_key` property
- Reads `OPENROUTER_API_KEY` from environment

### 3. `config/config.yaml`
- Added `use_openrouter` flag (default: false)
- Added `openrouter_base_url` for custom endpoints
- Updated model examples to show OpenRouter format

### 4. `config/.env.example`
- Added `OPENROUTER_API_KEY` documentation
- Clarified OpenAI vs OpenRouter choice

### 5. `src/main.py`
- Updated API key validation to check for OpenRouter key
- Shows which API is being used at startup

## Switching Between OpenAI and OpenRouter

You can switch between providers by just changing the config:

**Use OpenRouter:**
```yaml
use_openrouter: true
model: "anthropic/claude-3-sonnet"
```

**Use OpenAI:**
```yaml
use_openrouter: false
model: "gpt-4"
```

No code changes needed!

## Advanced Configuration

### Custom Base URL

If you're using a self-hosted OpenRouter instance or proxy:

```yaml
agent:
  use_openrouter: true
  model: "anthropic/claude-3-sonnet"
  openrouter_base_url: "https://your-custom-endpoint.com/v1"
```

### Rate Limiting

OpenRouter has generous rate limits, but you can add custom retry logic in `config.yaml`:

```yaml
agent:
  retry_attempts: 5
  timeout_seconds: 60
```

## Troubleshooting

### Error: "OPENROUTER_API_KEY not found"

**Solution:** Make sure you've set the key in `config/.env`:
```
OPENROUTER_API_KEY=sk-or-v1-...
```

### Error: "Invalid API key"

**Solution:** 
1. Check your key at https://openrouter.ai/keys
2. Make sure there are no extra spaces or quotes
3. Verify the key starts with `sk-or-v1-`

### Error: "Model not found"

**Solution:** Check model names at https://openrouter.ai/models

Use the exact identifier, e.g.:
- ✅ `anthropic/claude-3-sonnet`
- ❌ `claude-3-sonnet`

### Warning: "Insufficient credits"

**Solution:** Add credits to your OpenRouter account at https://openrouter.ai/credits

### Tool calling not working

**Solution:** Some models don't support function calling well. Use:
- ✅ Claude 3 models (Opus, Sonnet, Haiku)
- ✅ GPT-4 / GPT-3.5
- ⚠️ Llama models (limited support)
- ❌ Some smaller models

## Performance Comparison

Based on testing with this agentic assistant:

| Model | Speed | Tool Use | Cost | Recommendation |
|-------|-------|----------|------|----------------|
| Claude 3 Opus | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 💰💰💰 | Best quality |
| Claude 3 Sonnet | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 💰💰 | **Best overall** |
| GPT-4 Turbo | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 💰💰 | Great alternative |
| GPT-3.5 Turbo | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 💰 | Budget option |
| Llama 3 70B | ⭐⭐⭐⭐ | ⭐⭐ | Free | Testing only |

**Recommendation:** Start with `anthropic/claude-3-sonnet` for best results.

## Cost Estimation

Typical usage for this assistant:

| Scenario | Tokens | Model (Sonnet) | Cost |
|----------|--------|----------------|------|
| Single query | ~1,000 | Claude 3 Sonnet | $0.003 |
| 10-minute conversation | ~5,000 | Claude 3 Sonnet | $0.015 |
| 100 queries/day | ~100,000 | Claude 3 Sonnet | $0.30/day |

**Note:** OpenRouter charges per token, so cost varies based on usage.

## Benefits of Using OpenRouter

### 1. Model Flexibility
Switch between providers without code changes:
```yaml
model: "anthropic/claude-3-sonnet"  # Today
model: "openai/gpt-4-turbo"         # Tomorrow
```

### 2. Cost Optimization
- Use cheaper models for simple tasks
- Upgrade to premium models for complex reasoning
- Pay-as-you-go pricing

### 3. Automatic Fallbacks
OpenRouter can automatically try alternative models if one fails.

### 4. Unified Interface
One API key for all providers. No need to manage multiple accounts.

### 5. Transparent Pricing
See exact costs in real-time at https://openrouter.ai/activity

## Best Practices

### 1. Start with Claude 3 Sonnet
It has the best balance of speed, quality, and cost for agentic tasks.

### 2. Monitor Your Usage
Check https://openrouter.ai/activity regularly to track costs.

### 3. Set Budget Alerts
OpenRouter allows you to set spending limits.

### 4. Test with Free Models
Use Llama 3 for development and testing, then switch to premium models for production.

### 5. Use LangSmith for Monitoring
Enable LangSmith to trace and debug agent decisions:
```yaml
monitoring:
  langsmith_enabled: true
```

## Migration from OpenAI

If you're currently using OpenAI directly:

1. **Get OpenRouter API key** from https://openrouter.ai/keys
2. **Add to .env**: `OPENROUTER_API_KEY=sk-or-v1-...`
3. **Update config.yaml**: Set `use_openrouter: true`
4. **Choose model**: Use `openai/gpt-4-turbo` for identical behavior
5. **Test**: Run the application

That's it! No code changes needed.

## Support

- **OpenRouter Docs**: https://openrouter.ai/docs
- **Discord Community**: https://discord.gg/openrouter
- **Model Rankings**: https://openrouter.ai/rankings
- **API Status**: https://status.openrouter.ai

## FAQ

**Q: Can I use both OpenAI and OpenRouter?**
A: Yes! Just change `use_openrouter` in config.yaml and restart the app.

**Q: Which models support tool calling?**
A: Claude 3, GPT-4, GPT-3.5. Check model details on OpenRouter.

**Q: Is OpenRouter more expensive than direct API?**
A: Slightly (usually 10-20% markup), but you get multi-provider access and convenience.

**Q: Can I use free models?**
A: Yes! Llama 3, Mixtral, and other open-source models are available.

**Q: How do I monitor costs?**
A: Check https://openrouter.ai/activity for real-time usage and costs.

---

**You're now ready to use OpenRouter with your Personalized Agentic Assistant!** 🚀
