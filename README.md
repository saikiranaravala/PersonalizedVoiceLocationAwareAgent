# Personalized Agentic Assistant

A high-performance, voice-first AI assistant that bridges digital intelligence and physical actions through natural language understanding, real-time location awareness, and deep linking capabilities.

## 🎯 Project Overview

This agent acts as a "digital concierge" that:
- Understands natural voice commands
- Maintains user context (preferences and history)
- Executes real-world actions (booking rides, finding food, checking weather)
- Triggers external apps via Deep Linking or API calls

## 🏗️ Architecture

### Core Pillars

1. **Location Awareness**: Real-time GPS integration for contextual actions
2. **Extensible Tool-Use**: Atomic Tool pattern for easy service addition
3. **Deep Linking**: Universal Links to hand off to external apps
4. **Production Monitoring**: LangSmith integration for full observability

### Tech Stack

- **Python 3.11.9**: Core runtime
- **LangChain/LangGraph**: Agentic orchestration framework
- **OpenAI GPT-4 / OpenRouter**: Language model for reasoning (configurable)
- **Speech Recognition**: Google Speech-to-Text
- **pyttsx3**: Text-to-speech synthesis
- **LangSmith**: Production monitoring and tracing
- **Pytest**: Unit testing framework

> **New!** The project now supports **OpenRouter** for multi-provider LLM access (Claude, GPT-4, Llama, etc.). See [OPENROUTER_GUIDE.md](OPENROUTER_GUIDE.md) for setup.

## 📁 Project Structure

```
personalized-agentic-assistant/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── core.py              # Main agent orchestrator
│   │   └── prompts.py           # System prompts and templates
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py              # Base tool interface
│   │   ├── uber.py              # Uber deep linking
│   │   ├── zomato.py            # Restaurant search
│   │   ├── weather.py           # Weather information
│   │   └── location.py          # GPS utilities
│   ├── services/
│   │   ├── __init__.py
│   │   ├── speech.py            # STT/TTS handlers
│   │   └── context.py           # User context management
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   └── logger.py            # Logging utilities
│   └── main.py                  # Application entry point
├── tests/
│   ├── __init__.py
│   ├── test_tools.py            # Tool unit tests
│   ├── test_agent.py            # Agent integration tests
│   └── fixtures.py              # Test fixtures and mocks
├── config/
│   ├── config.yaml              # Main configuration
│   └── .env.example             # Environment variables template
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── pytest.ini                   # Pytest configuration
└── README.md                    # This file
```

## 🚀 Installation

### Prerequisites

- Windows 10 or Windows 11
- Python 3.11.9 installed
- Microphone access
- Internet connection

### Setup Steps

1. **Clone or extract the project**

2. **Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
copy config\.env.example config\.env
```

Edit `config\.env` with your API keys:
- `OPENAI_API_KEY`: Your OpenAI API key (for direct OpenAI usage)
- `OPENROUTER_API_KEY`: Your OpenRouter API key (for multi-provider access)
- `LANGSMITH_API_KEY`: Your LangSmith API key (optional)
- `ZOMATO_API_KEY`: Your Zomato API key (optional)

**Choose your LLM provider:**
- **OpenAI (default)**: Just add `OPENAI_API_KEY`
- **OpenRouter**: Add `OPENROUTER_API_KEY` and set `use_openrouter: true` in `config/config.yaml`

See [OPENROUTER_GUIDE.md](OPENROUTER_GUIDE.md) for OpenRouter setup and model options.

5. **Run the application**
```bash
python src/main.py
```

## 🎮 Usage

### Voice Commands

Start the application and speak naturally:

- **"Book me a cab to downtown"** - Opens Uber with destination
- **"I'm hungry, find Italian restaurants nearby"** - Searches and lists options
- **"What's the weather like?"** - Gets current weather for your location
- **"Book a ride to [restaurant name]"** - Chains restaurant search + Uber booking

### Command Line Interface

```bash
# Interactive voice mode (default)
python src/main.py

# Text-only mode (no voice)
python src/main.py --no-voice

# Debug mode with verbose logging
python src/main.py --debug

# Specify custom config file
python src/main.py --config path/to/config.yaml
```

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run specific test suites
```bash
# Test tools only
pytest tests/test_tools.py

# Test agent logic
pytest tests/test_agent.py

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Test with LangSmith Evaluators

The project includes evaluation datasets for testing accuracy:

```bash
python tests/run_evaluations.py
```

## 🔧 Configuration

### config.yaml

Key configuration options:

```yaml
agent:
  model: "gpt-4"
  temperature: 0.7
  max_iterations: 10

speech:
  recognition_engine: "google"
  tts_engine: "pyttsx3"
  language: "en-US"

location:
  use_gps: true
  fallback_location: "New York, NY"

monitoring:
  langsmith_enabled: true
  log_level: "INFO"
```

## 🛠️ Adding New Tools

To add a new service (e.g., Spotify):

1. Create `src/tools/spotify.py`:
```python
from tools.base import BaseTool

class SpotifyTool(BaseTool):
    name = "spotify_search"
    description = "Search and play music on Spotify"
    
    def execute(self, query: str, **kwargs):
        # Implementation
        pass
```

2. Register in `src/agent/core.py`:
```python
from tools.spotify import SpotifyTool
tools.append(SpotifyTool())
```

## 📊 Monitoring with LangSmith

View traces and debug agent decisions:

1. Enable LangSmith in config
2. Visit https://smith.langchain.com
3. Filter by project name: "personalized-agentic-assistant"

## 🐛 Troubleshooting

### Microphone not detected
- Check Windows Privacy Settings > Microphone
- Ensure default microphone is set in Sound Control Panel

### Speech recognition errors
- Check internet connection (Google STT requires online access)
- Speak clearly and reduce background noise
- Try adjusting microphone sensitivity

### API errors
- Verify API keys in `.env` file
- Check API quota/limits for your services
- Review logs in `logs/agent.log`

## 📝 Error Handling

The agent includes fallback mechanisms:

- **Zomato down**: Falls back to Google Maps search
- **GPS unavailable**: Uses configured fallback location
- **LLM timeout**: Retries with exponential backoff
- **Speech recognition failure**: Prompts for text input

## 🔒 Security Notes

- Never commit `.env` file with real API keys
- API keys are loaded from environment only
- User location data is not persisted
- All API calls are logged (disable in production if sensitive)

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📧 Support

For issues or questions, please open an issue on the project repository.

---

**Built with ❤️ as a production-ready AI assistant framework**
