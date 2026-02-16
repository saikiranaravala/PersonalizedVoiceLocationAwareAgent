# Architecture Documentation

## System Overview

The Personalized Agentic Assistant is built on a modular, production-ready architecture that separates concerns and enables easy extensibility.

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Voice Input  │  │  Text Input  │  │ Rich Console │      │
│  │   (STT)      │  │   (CLI)      │  │   Display    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Speech Service Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Speech Recognition (Google STT)                      │   │
│  │  Text-to-Speech (pyttsx3)                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Orchestration Layer                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         AgenticAssistant (Core Agent)                 │   │
│  │  - LangChain Agent Executor                          │   │
│  │  - OpenAI GPT-4 LLM                                  │   │
│  │  - Tool Selection & Execution                        │   │
│  │  - Context Management                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Tool Layer     │  │ Service Layer   │  │  Context Layer  │
│ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │
│ │ WeatherTool │ │  │ │  Location   │ │  │ │   Context   │ │
│ │             │ │  │ │   Service   │ │  │ │  Manager    │ │
│ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │
│ ┌─────────────┐ │  │ ┌─────────────┐ │  │ - Preferences │ │
│ │ ZomatoTool  │ │  │ │   Speech    │ │  │ - History     │ │
│ │             │ │  │ │   Service   │ │  │ - Location    │ │
│ └─────────────┘ │  │ └─────────────┘ │  │               │ │
│ ┌─────────────┐ │  │                 │  │               │ │
│ │  UberTool   │ │  │                 │  │               │ │
│ │             │ │  │                 │  │               │ │
│ └─────────────┘ │  │                 │  │               │ │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                    │
          ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   External Services Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  OpenAI API  │  │  Weather API │  │  Zomato API  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Geocoder  │  │  Deep Links  │  │  LangSmith   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agent Orchestration (agent/)

**AgenticAssistant** (`agent/core.py`)
- Central orchestrator using LangChain's Agent Executor
- Manages the agentic loop: Perception → Reasoning → Execution
- Handles tool selection and multi-step reasoning
- Integrates with LangSmith for observability

**Prompts** (`agent/prompts.py`)
- System prompts for agent behavior
- Response formatting templates
- Context injection patterns

### 2. Tool Layer (tools/)

**BaseTool** (`tools/base.py`)
- Abstract base class for all tools
- Standardized interface: validate → execute → handle_error
- Automatic LangChain tool conversion

**WeatherTool** (`tools/weather.py`)
- Fetches real-time weather data
- Uses Open-Meteo API (no key required)
- Location-aware (GPS or manual)

**ZomatoTool** (`tools/zomato.py`)
- Restaurant search and recommendations
- Optional Zomato API integration
- Mock data fallback for demos

**UberTool** (`tools/uber.py`)
- Generates Uber deep links
- Universal Link format for cross-platform
- Automatic pickup location (GPS)

### 3. Service Layer (services/)

**LocationService** (`services/location.py`)
- GPS location detection
- Geocoding (address → coordinates)
- Reverse geocoding (coordinates → address)
- Distance calculation (Haversine formula)
- Fallback location handling

**SpeechService** (`services/speech.py`)
- Speech-to-Text (Google Speech Recognition)
- Text-to-Speech (pyttsx3 engine)
- Microphone availability detection
- Ambient noise adjustment

**ContextManager** (`services/context.py`)
- User preference storage
- Conversation history management
- Location context maintenance
- Preference extraction from conversation

### 4. Utilities (utils/)

**Config** (`utils/config.py`)
- YAML configuration management
- Environment variable loading
- Dot-notation config access

**Logger** (`utils/logger.py`)
- Structured logging with Loguru
- Console and file output
- Rotation and compression

## Data Flow: Request Processing

### Example: "Book me a ride to Central Park"

1. **Input Layer**
   ```
   User speaks → Speech Service (STT) → Text: "Book me a ride to Central Park"
   ```

2. **Agent Reasoning**
   ```
   AgenticAssistant receives text
   → Adds to conversation history
   → Gets current GPS location
   → Injects context into prompt
   → Sends to GPT-4: "User wants ride to Central Park"
   ```

3. **Tool Selection**
   ```
   LLM reasons: "Need to use book_uber_ride tool"
   → Identifies destination: "Central Park"
   → Uses current location for pickup
   ```

4. **Tool Execution**
   ```
   UberTool.execute(destination="Central Park")
   → LocationService.get_current_location() → (lat, lng)
   → LocationService.geocode_address("Central Park") → (dest_lat, dest_lng)
   → Generate deep link: "https://m.uber.com/ul/?action=setPickup&..."
   ```

5. **Response Generation**
   ```
   Tool returns: {success: True, deep_link: "...", message: "..."}
   → LLM formats response
   → ContextManager records interaction
   → Speech Service (TTS) speaks response
   ```

6. **Output Layer**
   ```
   Console displays: "Uber link generated..."
   Deep link displayed: [clickable URL]
   Speaker plays: "Uber link generated from your location to Central Park"
   ```

## Extensibility: Adding a New Tool

### Example: Adding Spotify Integration

1. **Create Tool Class** (`tools/spotify.py`)
```python
from tools.base import BaseTool

class SpotifyTool(BaseTool):
    name = "play_music"
    description = "Search and play music on Spotify"
    
    def execute(self, query: str, **kwargs):
        # Implementation
        spotify_link = f"spotify:search:{query}"
        return {
            "success": True,
            "deep_link": spotify_link,
            "message": f"Playing {query} on Spotify"
        }
```

2. **Register Tool** (in `agent/core.py`)
```python
from tools.spotify import SpotifyTool

def _initialize_tools(self):
    tools = []
    # ... existing tools ...
    
    spotify_tool = SpotifyTool()
    tools.append(spotify_tool.to_langchain_tool())
    
    return tools
```

3. **Test Tool** (`tests/test_tools.py`)
```python
def test_spotify_tool():
    tool = SpotifyTool()
    result = tool.execute(query="jazz music")
    assert result["success"] is True
```

That's it! The agent will automatically:
- Recognize when to use the tool
- Call it with appropriate parameters
- Handle errors gracefully

## Design Patterns

### 1. Atomic Tool Pattern
- Each tool is a self-contained, testable unit
- Tools have single responsibility
- Easy to mock for testing
- Can be composed into complex workflows

### 2. Service Layer Pattern
- Business logic separated from tools
- Shared services (location, speech) used across tools
- Promotes code reuse

### 3. Context Injection Pattern
- User context dynamically injected into prompts
- LLM has access to location, preferences, history
- Enables personalized responses

### 4. Chain of Responsibility
- Agent → Tool Selection → Tool Execution → Response
- Each layer handles its specific concern
- Easy to trace and debug

## Error Handling Strategy

### 1. Tool Level
```python
try:
    result = api_call()
    return {"success": True, "data": result}
except APIError as e:
    return {"success": False, "error": str(e)}
```

### 2. Service Level
```python
try:
    location = get_gps()
except GPSError:
    location = get_fallback_location()
```

### 3. Agent Level
```python
try:
    response = agent.invoke(input)
except Exception as e:
    return fallback_response
    log_error(e)
```

### 4. Application Level
```python
try:
    run_voice_mode()
except KeyboardInterrupt:
    graceful_shutdown()
except Exception:
    display_error()
    log_and_report()
```

## Monitoring & Observability

### LangSmith Integration
- Traces every agent decision
- Records tool inputs/outputs
- Tracks token usage
- Enables debugging of reasoning chains

### Logging Strategy
- **INFO**: User interactions, tool executions
- **WARNING**: Fallbacks, degraded service
- **ERROR**: API failures, exceptions
- **DEBUG**: Detailed execution flow

### Metrics to Monitor
- Request success rate
- Average response time
- Tool execution frequency
- Error rates by type
- GPS accuracy

## Testing Strategy

### 1. Unit Tests
- Individual tools in isolation
- Mock external APIs
- Test error handling

### 2. Integration Tests
- Tool + Service interaction
- Agent + Tool execution
- End-to-end workflows

### 3. Evaluation Tests (LangSmith)
- 50+ test cases with different accents
- Various location scenarios
- Edge cases (no GPS, API down)

## Production Considerations

### Security
- API keys in environment variables
- Input sanitization
- Rate limiting (future)
- No PII in logs

### Performance
- Connection pooling
- Response caching (future)
- Async tool execution (future)
- Lazy loading of services

### Reliability
- Automatic retries with backoff
- Fallback mechanisms
- Graceful degradation
- Health checks (future)

### Scalability
- Stateless agent design
- Horizontal scaling possible
- Database for preferences (future)
- Queue for async tasks (future)

## Configuration Management

### YAML Configuration
```yaml
agent:
  model: "gpt-4"
  temperature: 0.7
  
tools:
  enabled:
    - weather
    - uber
    - zomato
```

### Environment Variables
```
OPENAI_API_KEY=sk-...
LANGSMITH_API_KEY=...
```

### Runtime Configuration
- Can be overridden via command line
- Hot reload not supported (requires restart)

## Future Enhancements

### Planned Features
1. **More Tools**: Calendar, Email, Maps
2. **User Authentication**: Multi-user support
3. **Database Integration**: PostgreSQL for preferences
4. **Web Interface**: FastAPI + React frontend
5. **Mobile App**: Native iOS/Android
6. **Async Processing**: Celery task queue
7. **Caching**: Redis for API responses
8. **Analytics**: Usage tracking dashboard

### Architecture Evolution
- Microservices for heavy tools
- Event-driven architecture
- GraphQL API layer
- Kubernetes deployment

---

**This architecture prioritizes: Modularity, Testability, Extensibility, and Production-Readiness**
