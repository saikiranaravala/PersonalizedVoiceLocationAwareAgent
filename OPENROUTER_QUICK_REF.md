# OpenRouter Quick Reference Card

## 🚀 Quick Setup (3 Steps)

### 1. Get API Key
```
Visit: https://openrouter.ai/keys
Copy your key: sk-or-v1-xxxxx...
```

### 2. Configure
```bash
# Edit config/.env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

```yaml
# Edit config/config.yaml
agent:
  use_openrouter: true
  model: "anthropic/claude-3-sonnet"
```

### 3. Run
```bash
python src/main.py
```

---

## 📋 Recommended Models

| Use Case | Model | Identifier |
|----------|-------|------------|
| 🏆 **Best Overall** | Claude 3 Sonnet | `anthropic/claude-3-sonnet` |
| 💎 **Highest Quality** | Claude 3 Opus | `anthropic/claude-3-opus` |
| ⚡ **Fastest** | Claude 3 Haiku | `anthropic/claude-3-haiku` |
| 💰 **Budget** | GPT-3.5 Turbo | `openai/gpt-3.5-turbo` |
| 🆓 **Free/Testing** | Llama 3 70B | `meta-llama/llama-3-70b-instruct` |

---

## 🔄 Switching Providers

### Use OpenRouter (Multi-provider)
```yaml
use_openrouter: true
model: "anthropic/claude-3-sonnet"
```

### Use OpenAI Direct (Original)
```yaml
use_openrouter: false
model: "gpt-4"
```

---

## 💵 Cost Comparison (per 1M tokens)

| Model | Input | Output | Total (avg) |
|-------|-------|--------|-------------|
| Claude 3 Haiku | $0.25 | $1.25 | ~$0.75 |
| Claude 3 Sonnet | $3.00 | $15.00 | ~$9.00 |
| GPT-3.5 Turbo | $0.50 | $1.50 | ~$1.00 |
| GPT-4 Turbo | $10.00 | $30.00 | ~$20.00 |
| Llama 3 70B | $0.59 | $0.79 | ~$0.69 |

**Typical query cost:** $0.001 - $0.01

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Add `OPENROUTER_API_KEY` to `config/.env` |
| "Invalid model" | Check exact name at openrouter.ai/models |
| Tool calling fails | Use Claude 3 or GPT-4 models |
| "Insufficient credits" | Add credits at openrouter.ai/credits |

---

## 📊 What Changed in the Code

✅ `src/agent/core.py` - Added OpenRouter support
✅ `src/utils/config.py` - Added API key handling
✅ `config/config.yaml` - Added configuration options
✅ `config/.env.example` - Added key examples
✅ `src/main.py` - Updated validation

**No breaking changes!** Original OpenAI mode still works.

---

## 🔗 Useful Links

- **Get API Key**: https://openrouter.ai/keys
- **Model List**: https://openrouter.ai/models
- **Usage Dashboard**: https://openrouter.ai/activity
- **Documentation**: https://openrouter.ai/docs
- **Status**: https://status.openrouter.ai

---

## 💡 Pro Tips

1. **Start with Claude 3 Sonnet** - Best tool use performance
2. **Monitor costs** - Check openrouter.ai/activity
3. **Test with Llama** - Free for development
4. **Use LangSmith** - Enable for debugging
5. **Set budget limits** - Prevent overspending

---

**See OPENROUTER_GUIDE.md for complete documentation**
