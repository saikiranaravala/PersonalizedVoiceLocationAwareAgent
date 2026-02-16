# Quick Start Guide

## Get Started in 5 Minutes

### 1. Setup (First Time Only)

```bash
# Install Python 3.11.9 if not already installed
# Download from: https://www.python.org/downloads/release/python-3119/

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create configuration file
copy config\.env.example config\.env

# Edit config\.env and add your OpenAI API key
notepad config\.env
```

### 2. Run the Assistant

**Easiest way:**
```bash
start.bat
```

**Or manually:**
```bash
venv\Scripts\activate
python src\main.py
```

### 3. Try These Commands

**Voice Mode** (speak these):
- "What's the weather like?"
- "Find Italian restaurants nearby"
- "Book me an Uber to Times Square"
- "I'm hungry, find a good restaurant and get me a ride there"

**Text Mode** (type these):
- Type your command instead of speaking
- Type `help` for more commands
- Type `quit` to exit

## Example Interactions

### 🌤️ Check Weather
```
You: "What's the weather?"
Assistant: "Current weather in New York: Clear sky, 72°F"
```

### 🍕 Find Restaurants
```
You: "Find Italian restaurants nearby"
Assistant: "I found 5 great options:
1. Bella Italia - Italian (Rating: 4.5)
2. Pasta Paradise - Italian (Rating: 4.3)
3. Trattoria Roma - Italian (Rating: 4.7)"
```

### 🚗 Book a Ride
```
You: "Book me a ride to Central Park"
Assistant: "Uber ride link generated from your location to Central Park.
Click the link to open Uber app and confirm your ride."
[Link appears]: https://m.uber.com/ul/?action=setPickup&...
```

### 🍽️ Combined Request
```
You: "I'm hungry, get me a ride to a good Italian place"
Assistant: "Let me find Italian restaurants near you first...
I found 3 great options. Which would you like to go to?
1. Bella Italia - 4.5 stars
2. Pasta Paradise - 4.3 stars
3. Trattoria Roma - 4.7 stars"

You: "The first one"
Assistant: "Great choice! Generating Uber link to Bella Italia..."
[Uber link appears]
```

## Configuration Options

### Text-Only Mode
If microphone is unavailable or you prefer typing:
```bash
python src\main.py --no-voice
```

### Debug Mode
For troubleshooting:
```bash
python src\main.py --debug
```

### Custom Config
Use a different configuration file:
```bash
python src\main.py --config path\to\config.yaml
```

## Common Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `quit` or `exit` | Close the application |
| `reset` | Clear conversation history |
| `test` | Test microphone (voice mode) |
| `text` | Switch to text-only mode |

## Keyboard Shortcuts

- **Enter** (voice mode): Start speaking
- **Type and Enter**: Use text instead of voice
- **Ctrl+C**: Interrupt current operation

## Tips for Best Results

### Voice Commands
1. **Speak clearly** and at normal pace
2. **Wait** for "Listening..." prompt
3. **Minimize background noise**
4. **Be specific**: "Italian restaurant in Brooklyn" vs "food"

### Location
- System automatically uses your GPS location
- You can override: "Find restaurants in Manhattan"
- Specify addresses: "Book a ride to 123 Main St"

### Context
- The assistant remembers your conversation
- It maintains preferences over time
- Use `reset` to start fresh

## Troubleshooting

### "No microphone detected"
→ Check Windows microphone settings
→ Run `python src\main.py --no-voice` for text mode

### "OpenAI API key not found"
→ Edit `config\.env` and add: `OPENAI_API_KEY=sk-...`

### "Speech recognition failed"
→ Check internet connection (Google STT requires online)
→ Speak more clearly or adjust microphone volume

### "Module not found"
→ Activate virtual environment: `venv\Scripts\activate`
→ Install dependencies: `pip install -r requirements.txt`

## API Key Setup

### Required: OpenAI
1. Go to: https://platform.openai.com/api-keys
2. Create API key
3. Add to `config\.env`: `OPENAI_API_KEY=sk-...`

### Optional: LangSmith (for monitoring)
1. Go to: https://smith.langchain.com
2. Create API key
3. Add to `config\.env`: `LANGSMITH_API_KEY=...`

### Optional: Zomato (for real restaurant data)
1. Go to: https://developers.zomato.com/api
2. Get API key
3. Add to `config\.env`: `ZOMATO_API_KEY=...`

Without Zomato key, the app uses mock data for demonstration.

## Next Steps

1. **Explore Features**: Try different voice commands
2. **Customize**: Edit `config/config.yaml` for preferences
3. **Add Tools**: See README.md for adding new services
4. **Monitor**: Enable LangSmith to trace agent decisions
5. **Test**: Run `pytest` to verify functionality

## Support

- Full documentation: See README.md
- Installation help: See INSTALL_WINDOWS.md
- Logs: Check `logs/agent.log`
- Issues: Review console output

---

**Ready to start? Run `start.bat` and say hello!** 👋
