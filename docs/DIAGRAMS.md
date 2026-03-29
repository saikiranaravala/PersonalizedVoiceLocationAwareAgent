# System Architecture Diagrams — Personalized Agentic Voice Assistant v2.0

This document contains all Mermaid diagrams for system architecture, data flow, and user journeys.

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Data Flow Diagrams](#2-data-flow-diagrams)
3. [User Journeys](#3-user-journeys)
4. [Component Diagrams](#4-component-diagrams)
5. [Deployment Architecture](#5-deployment-architecture)
6. [State Diagrams](#6-state-diagrams)
7. [Entity Relationship](#7-entity-relationship)
8. [Sequence Diagrams](#8-sequence-diagrams)
9. [Activity Diagrams](#9-activity-diagrams)
10. [Network Architecture](#10-network-architecture)

---

## 1. System Architecture

### 1.1 High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
        B[React App]
        C[Voice Input<br/>30s timeout]
        D[User Profile<br/>localStorage]
        IP[ipify.org<br/>client IP on mount]
    end

    subgraph "Backend Layer"
        E[FastAPI Server]
        F[WebSocket Manager<br/>X-Forwarded-For]
        G[LangChain Agent<br/>create_tool_calling_agent]
        H[LocationContextAdapter]
    end

    subgraph "Tool Layer"
        I[Weather Tool<br/>Open-Meteo]
        J[Restaurant Tool<br/>Overpass API]
        K[Uber Tool<br/>deep link]
        L[Events Tool<br/>Ticketmaster v2]
        M[Save Tools<br/>ws_sender action]
    end

    subgraph "Service Layer"
        N[LocationService<br/>get_current_location<br/>client_ip param]
        O[ContextManager<br/>profile coords cache]
    end

    subgraph "External Services"
        P[OpenRouter / OpenAI<br/>LLM]
        Q[Nominatim<br/>geocoding, 1/sec]
        R[Overpass API<br/>OSM, free]
        S[Open-Meteo<br/>weather, free]
        T[Ticketmaster<br/>Discovery API v2]
        U[ipinfo.io<br/>IP → city]
        V[Uber deep link]
    end

    A --> B
    B --> C
    B <--> D
    B --> IP
    IP -->|clientIpRef| B
    B <-->|WebSocket<br/>message + user_profile + client_ip| F
    F <--> E
    E --> G
    G --> H
    H --> N
    H --> O
    G --> I
    G --> J
    G --> K
    G --> L
    G --> M
    G <-->|API| P
    I <--> S
    J <--> R
    J <--> Q
    K --> V
    L <--> T
    N <--> Q
    N <--> U

    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style E fill:#fff4e1
    style G fill:#f0e1ff
    style P fill:#ffe1e1
```

### 1.2 Location Resolution Priority Chain

```mermaid
flowchart TD
    A[Request arrives with user_profile + client_ip] --> B{Profile has lat/lon?}
    B -->|Yes| Z[Use coords directly ✅]
    B -->|No| C{Profile has address/city/state?}
    C -->|Yes| D[Nominatim geocode<br/>sleep 1.1s + 429 retry]
    D --> E{Geocode succeeded?}
    E -->|Yes| Z
    E -->|No| F{client_ip provided?}
    C -->|No| F
    F -->|Yes| G[ipinfo.io geolocate<br/>client_ip]
    G --> H{IP resolved?}
    H -->|Yes| Z
    H -->|No| I[config fallback_location<br/>absolute last resort]
    F -->|No| I
    I --> Z

    classDef never fill:#ffe1e1,stroke:#c00
    classDef good fill:#e1ffe1,stroke:#090
    classDef warn fill:#fff4e1,stroke:#a80
    class Z good
    class I warn
```

### 1.3 Component Architecture

```mermaid
graph LR
    subgraph "Frontend Components"
        A[App.tsx<br/>linkifyText + 4 chips]
        B[useVoiceAssistant<br/>ipify + WS + TTS]
        C[useUserProfile<br/>localStorage]
        D[WebSocket Client<br/>client.ts]
        E[ProfileSetup<br/>3-step modal]
        F[ProfileSettings<br/>edit + danger zone]
        V[VoiceButton<br/>push-to-talk / manual]
    end

    subgraph "Backend Components"
        G[api_server.py<br/>X-Forwarded-For]
        H[AgenticAssistant<br/>agent/core.py]
        LC[LocationContextAdapter]
        I[BaseTool]
        J[WeatherTool]
        K[RestaurantFinder<br/>Overpass + Nominatim]
        L[UberTool]
        EV[EventsTool<br/>Ticketmaster v2]
        SV[SaveTools<br/>ws_sender]
        M[LocationService<br/>client_ip param]
        N[ContextManager]
    end

    A --> B
    A --> C
    A --> V
    B --> D
    C --> localStorage
    D <-->|WS payload<br/>+client_ip| G
    G --> H
    H --> LC
    LC --> N
    LC --> M
    H --> J
    H --> K
    H --> L
    H --> EV
    H --> SV
    J --> I
    K --> I
    L --> I
    EV --> I
    SV --> I
    K --> M
    J --> M
    L --> M
```

---

## 2. Data Flow Diagrams

### 2.1 Complete Message Flow

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Browser
    participant WebSocket
    participant FastAPI
    participant Agent
    participant Tool
    participant ExternalAPI

    Note over Browser: On mount: fetch ipify.org → clientIpRef
    User->>Browser: Speak / type message
    Browser->>Browser: Load user_profile from localStorage
    Browser->>WebSocket: { message, user_profile, client_ip, user_agent, timestamp }
    WebSocket->>FastAPI: Forward WebSocket frame
    FastAPI->>FastAPI: Extract client_ip from X-Forwarded-For header
    FastAPI->>Agent: process_request(msg, user_profile, client_ip)
    Agent->>Agent: _extract_location_from_profile → Nominatim geocode
    Agent->>Agent: Inject [SYSTEM CONTEXT — User location] into prompt
    Agent->>Agent: LLM selects appropriate tool
    Agent->>Tool: execute(params)
    Tool->>Tool: _resolve_location → profile coords
    Tool->>ExternalAPI: Overpass / Open-Meteo / Ticketmaster
    ExternalAPI-->>Tool: Raw data
    Tool-->>Agent: Formatted result dict
    Agent-->>FastAPI: { output: "...", intermediate_steps: [...] }
    FastAPI-->>WebSocket: { type: "response", message: "...", success: true }
    WebSocket-->>Browser: Deliver response
    Browser->>Browser: linkifyText() → [label](url) → <a> tags
    Browser->>Browser: Speech Synthesis (TTS)
    Browser->>User: Display text + speak aloud
```

### 2.2 Client IP Pipeline

```mermaid
flowchart LR
    A["Browser mount\nfetch('https://api.ipify.org')\n→ clientIpRef"] -->|WS payload\nclient_ip field| B["api_server.py\nX-Forwarded-For\nX-Real-IP\n→ client_ip var"]
    B -->|process_request\nclient_ip param| C["agent/core.py\nlocation_adapter._client_ip\nlocation_service._client_ip"]
    C -->|get_current_location\nclient_ip param| D["services/location.py\ngeocoder.ip(client_ip)\n→ ipinfo.io"]
    D --> E["City, State, Lat/Lon\nfor user's real location ✅"]

    style E fill:#e1ffe1
```

### 2.3 Profile Data Flow

```mermaid
flowchart TD
    A[User Opens App] --> B{Profile Exists?}
    B -->|No| C[Show ProfileSetup Modal]
    B -->|Yes| D[Load Profile from localStorage]

    C --> E[Step 1: Name]
    E --> F[Step 2: Gender, Age, Title]
    F --> G[Step 3: Address, City, State, Country]
    G --> H[Save to localStorage]
    H --> D

    D --> I[useVoiceAssistant hook]
    I --> IP[fetch ipify.org → clientIpRef]
    I --> J[Store in userProfileRef]
    J --> K[User sends message]
    K --> L[Include user_profile + client_ip in WebSocket]
    L --> M[Backend: geocode profile address → lat/lon]
    M --> N[Agent: inject location context into prompt]
    N --> O[Tools: use profile coords for API calls]

    style C fill:#ffe1e1
    style H fill:#e1ffe1
    style M fill:#e1f5ff
```

### 2.4 Uber Smart Pickup Flow

```mermaid
flowchart TD
    A["User: 'Book Uber to mall'"] --> B[Backend receives request]
    B --> C[Extract user_agent]
    C --> D{Device Type?}

    D -->|Mobile iPhone / Android| E[Let Uber app use GPS]
    D -->|Desktop Windows / Mac / Linux| F{Profile has address?}

    F -->|Yes| G[Build complete address string]
    F -->|No| H[Use city coordinates]

    G --> I["street + city + state + country\n'5013 Burgundy Dr, Erie, PA, USA'"]
    I --> J[Nominatim geocode]
    J --> K["Pickup coords\n(42.068, -80.123)"]

    K --> N[Generate Uber deep link]
    E --> N
    H --> N

    N --> O["https://m.uber.com/ul/?action=setPickup\n&pickup[lat]=42.068&pickup[lng]=-80.123\n&dropoff[lat]=..."]

    O --> P[Return link to user]
    P --> Q[SaveUberTripTool → ws_sender → action msg]
    Q --> R[App.tsx onAction → addUberTrip → localStorage]

    style D fill:#fff4e1
    style G fill:#e1ffe1
    style O fill:#e1f5ff
    style R fill:#f0e1ff
```

### 2.5 Events Discovery Flow

```mermaid
flowchart TD
    A["User: 'What events are near me?'"] --> B[find_local_events called]
    B --> C[Resolve city + state from profile]
    C --> D["State normalisation\n'PENNSYLVANIA' → 'PA'"]
    D --> E["Ticketmaster Discovery API v2\ncountryCode=US, stateCode=PA, city=Erie\nsort=date,asc, size=20\nstartDate=now, endDate=now+30days"]
    E --> F[_parse_events]
    F --> G["name, date, venue, address\ncategory, price, url\nNO image_url field"]
    G --> H["display_limit = max(10, int(limit))\nEnforce minimum 10"]
    H --> I["LLM formats:\n1. [Event Name](url) at Venue on Date"]
    I --> J["linkifyText: [label](url) → <a>label</a>\nNo trailing )"]
    J --> K[User sees 10+ clean clickable links]

    style H fill:#fff4e1
    style J fill:#e1ffe1
    style K fill:#e1f5ff
```

---

## 3. User Journeys

### 3.1 First-Time User Journey

```mermaid
journey
    title First-Time User Experience
    section Arrival
      Open app: 5: User
      See profile setup modal: 5: User
    section Profile Setup
      Enter name: 4: User
      Choose gender & age: 4: User
      Enter address and city: 4: User
      Complete setup: 5: User
    section First Interaction
      Click microphone: 5: User
      Ask question (30s window): 5: User
      Receive spoken answer: 5: User
      Click quick-action chip: 5: User
```

### 3.2 Weather Check Journey

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Listening: Click mic or hold push-to-talk
    Listening --> AutoStop: 30s VOICE_TIMEOUT_MS
    Listening --> Processing: User clicks Stop & Send
    AutoStop --> Processing: Transcript sent
    Processing --> GeocodingProfile: _extract_location_from_profile
    GeocodingProfile --> FetchingWeather: Agent calls WeatherTool
    FetchingWeather --> FormatResponse: Open-Meteo returns data
    FormatResponse --> Speaking: TTS speaks response
    Speaking --> Idle: Complete
    Idle --> [*]
```

### 3.3 Restaurant Search Journey

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Listening: User speaks
    Listening --> Processing: "Find Italian restaurants near me"
    Processing --> GeocodingProfile: Nominatim geocodes Erie, PA
    GeocodingProfile --> OverpassQuery: (42.1292, -80.0851) radius 3000m
    OverpassQuery --> SortResults: Sort by distance
    SortResults --> FormatResponse: Top 5 nearest
    FormatResponse --> RenderLinks: linkifyText cleans markdown
    RenderLinks --> Speaking: TTS reads names
    Speaking --> Idle: Complete
    Idle --> [*]
```

---

## 4. Component Diagrams

### 4.1 Frontend Component Tree

```mermaid
graph TD
    A[App.tsx] --> B[useUserProfile]
    A --> C[useVoiceAssistant]
    A --> D[Status Indicator]
    A --> E[Conversation Display<br/>linkifyText]
    A --> F[VoiceButton<br/>push-to-talk / manual]
    A --> G["Quick Actions (4 chips)\nWeather · Restaurants · Ride · Events"]
    A --> H[ProfileSetup Modal]
    A --> I[ProfileSettings Modal]

    B --> K[localStorage]
    C --> L[WebSocket Client<br/>client.ts]
    C --> IP[ipify.org fetch<br/>on mount]
    H --> M[Step 1: Name]
    H --> N[Step 2: Personal info]
    H --> O[Step 3: Address / Location]
    I --> P[Basic Info Section]
    I --> Q[Location Section]
    I --> R[Danger Zone — reset]

    style A fill:#e1f5ff
    style B fill:#ffe1e1
    style C fill:#ffe1e1
    style H fill:#f0e1ff
    style I fill:#f0e1ff
```

### 4.2 Backend Tool Architecture

```mermaid
classDiagram
    class BaseTool {
        +name: str
        +description: str
        +execute(**kwargs) Dict
        +validate_inputs(**kwargs) bool
        +handle_error(e) Dict
    }

    class WeatherTool {
        -location_adapter: LocationContextAdapter
        +execute(location: str) Dict
        -_fetch_weather(lat, lon) Dict
    }

    class RestaurantFinder {
        -location_service: LocationContextAdapter
        +execute(query: str, location: Union[str,dict,None]) Dict
        -_resolve_location(location) Tuple
        -_geocode_city(city: str) Tuple
        -_profile_address_from_service() Tuple
        -_overpass_query(lat, lon, radius) List
    }

    class UberTool {
        -location_service: LocationContextAdapter
        +execute(destination: str, user_agent: str, user_profile: dict) Dict
        -_build_complete_address(profile) str
        -_generate_deep_link(pickup_lat, pickup_lon, drop_lat, drop_lon) str
    }

    class EventsTool {
        -api_key: str
        -location_adapter: LocationContextAdapter
        +execute(city: str, state_code: str, keyword: str, limit: int) Dict
        -_parse_events(events) List
        -_state_to_code(state: str) str
        -_keyword_to_segment_id(keyword: str) str
    }

    class SaveRestaurantTool {
        -ws_sender: Callable
        +execute(name: str, address: str, cuisine: str) Dict
    }

    class SaveUberTripTool {
        -ws_sender: Callable
        +execute(destination: str, address: str, purpose: str) Dict
    }

    class LocationContextAdapter {
        -_ctx: ContextManager
        -_fallback: LocationService
        -_client_ip: str
        +get_location() Dict
        +get_current_location(client_ip: str) Dict
    }

    class LocationService {
        -_client_ip: str
        -_geocode_cache: Dict
        +get_current_location(client_ip: str) Dict
        +geocode_address(address: str) Tuple
        +reverse_geocode(lat, lon) str
        +get_distance(lat1, lon1, lat2, lon2) float
    }

    BaseTool <|-- WeatherTool
    BaseTool <|-- RestaurantFinder
    BaseTool <|-- UberTool
    BaseTool <|-- EventsTool
    BaseTool <|-- SaveRestaurantTool
    BaseTool <|-- SaveUberTripTool
    WeatherTool --> LocationContextAdapter
    RestaurantFinder --> LocationContextAdapter
    UberTool --> LocationContextAdapter
    EventsTool --> LocationContextAdapter
    LocationContextAdapter --> LocationService
```

### 4.3 Agent Decision Flow

```mermaid
flowchart TD
    A[User Message Received] --> B[Inject location context hint]
    B --> C[LLM processes with context]
    C --> D{Intent Detection}

    D -->|Weather query| E[WeatherTool]
    D -->|Restaurant query| F[RestaurantFinder]
    D -->|Ride / Uber query| G[UberTool]
    D -->|Events query| H[EventsTool]
    D -->|Save restaurant| I[SaveRestaurantTool]
    D -->|Save trip| J[SaveUberTripTool]
    D -->|General question| K[Direct LLM Response]

    E --> L[LocationContextAdapter]
    F --> L
    G --> L
    H --> L

    L --> M{Priority chain}
    M -->|Profile coords| N[Use directly ✅]
    M -->|Profile address| O[Nominatim geocode]
    M -->|client_ip| P[ipinfo.io geolocate]

    O --> Q[Execute Tool]
    N --> Q
    P --> Q

    I --> R[ws_sender action msg]
    J --> R

    Q --> S[Format Response]
    K --> S
    R --> T[Frontend localStorage]

    S --> U[Return to User]

    style D fill:#fff4e1
    style Q fill:#e1ffe1
    style U fill:#e1f5ff
```

---

## 5. Deployment Architecture

### 5.1 Development Environment

```mermaid
graph LR
    subgraph "Developer Machine"
        A[VS Code]
        B[Terminal 1<br/>python api_server.py]
        C[Terminal 2<br/>npm run dev]
    end

    subgraph "Local Services"
        D[FastAPI<br/>:8000]
        E[Vite Dev Server<br/>:5173]
        F[Browser<br/>localhost:5173]
    end

    subgraph "External APIs"
        G[OpenRouter / OpenAI]
        H[Open-Meteo]
        I[Overpass API]
        J[Nominatim]
        K[Ticketmaster]
        L[ipify.org / ipinfo.io]
    end

    A --> B
    A --> C
    B --> D
    C --> E
    E --> F
    F <-->|ws://localhost:8000/ws/{id}| D
    D <--> G
    D <--> H
    D <--> I
    D <--> J
    D <--> K
    F <-->|HTTPS| L
```

### 5.2 Production Deployment (Render)

```mermaid
graph TB
    subgraph "Static Frontend (Render)"
        A[React Build<br/>ui/dist]
        B[_redirects<br/>SPA routing]
    end

    subgraph "Web Service (Render)"
        C[uvicorn<br/>api_server:app]
        LB[Render Load Balancer<br/>X-Forwarded-For set]
    end

    subgraph "Monitoring"
        I[LangSmith<br/>agent traces]
    end

    Users -->|HTTPS| A
    Users -->|WSS| LB
    LB --> C
    C --> I
```

### 5.3 Nginx Self-Hosted

```mermaid
graph LR
    subgraph "Nginx"
        A[SSL Termination]
        B[WebSocket Upgrade<br/>proxy_set_header Upgrade]
        C[X-Forwarded-For<br/>proxy_add_x_forwarded_for]
    end

    subgraph "Backend"
        D[FastAPI :8000]
    end

    Users -->|HTTPS / WSS| A
    A --> B
    B --> C
    C -->|HTTP / WS| D
```

### 5.4 Data Flow in Production

```mermaid
flowchart LR
    A[User Browser] -->|HTTPS + WSS| B[CDN / Load Balancer<br/>sets X-Forwarded-For]
    B --> C[FastAPI Pod<br/>extracts client_ip]
    C -->|agent traces| D[LangSmith]
    C <-->|geocoding| E[Nominatim]
    C <-->|restaurants| F[Overpass API]
    C <-->|weather| G[Open-Meteo]
    C <-->|events| H[Ticketmaster]
    C <-->|LLM| I[OpenRouter / OpenAI]

    style A fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#f0e1ff
```

---

## 6. State Diagrams

### 6.1 Application State

```mermaid
stateDiagram-v2
    [*] --> Loading
    Loading --> ProfileSetup: No profile found
    Loading --> ResolvingIP: Has profile

    ResolvingIP --> Connected: ipify.org → clientIpRef

    ProfileSetup --> Step1
    Step1 --> Step2: Next
    Step2 --> Step3: Next
    Step3 --> ProfileComplete: Complete
    ProfileComplete --> ResolvingIP

    Connected --> Idle
    Idle --> Listening: User activates voice
    Listening --> AutoStop: 30s VOICE_TIMEOUT_MS
    AutoStop --> Processing: Transcript sent
    Listening --> Processing: Stop & Send clicked
    Processing --> Idle: Response received

    Idle --> Error: Connection lost
    Error --> Reconnecting: Auto retry (exponential backoff)
    Reconnecting --> Connected: Success
    Reconnecting --> Error: Max retries (5) exceeded

    Connected --> [*]: User closes app
```

### 6.2 WebSocket Connection State

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Connecting: connect()
    Connecting --> Connected: onopen
    Connecting --> Failed: onerror
    Connected --> Disconnected: onclose
    Connected --> Disconnected: Network error
    Failed --> Reconnecting: Auto retry (exponential backoff)
    Reconnecting --> Connecting: Attempt (max 5)
    Reconnecting --> Disconnected: Max retries exceeded
    Connected --> [*]: User closes app
```

### 6.3 Voice Recording State

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> PushToTalk: User holds mic button
    Idle --> ManualMode: User clicks mic
    PushToTalk --> Recording: pointerdown
    ManualMode --> Recording: click
    Recording --> Stopped: User releases (push-to-talk)
    Recording --> Stopped: User clicks Stop & Send
    Recording --> AutoStopped: VOICE_TIMEOUT_MS = 30s
    Stopped --> Sending: Transcript ready
    AutoStopped --> Sending: Transcript ready
    Sending --> Idle: Message dispatched
    Recording --> Error: Mic permission denied
    Error --> Idle: User resolves
```

---

## 7. Entity Relationship

### 7.1 User Profile Data Model

```mermaid
erDiagram
    USER_PROFILE ||--o{ RESTAURANT_VISIT : tracks
    USER_PROFILE ||--o{ UBER_TRIP : tracks
    USER_PROFILE ||--|| USER_PREFERENCES : has

    USER_PROFILE {
        string id PK
        string firstName
        string lastName
        string gender
        int age
        string title
        string address
        string city
        string state
        string country
        datetime createdAt
        datetime lastUpdatedAt
    }

    USER_PREFERENCES {
        string userId FK
        array favoriteRestaurants
        array frequentDestinations
        array preferredCuisines
    }

    RESTAURANT_VISIT {
        string id PK
        string userId FK
        string name
        string address
        string cuisine
        int rating
        string notes
        datetime visitDate
    }

    UBER_TRIP {
        string id PK
        string userId FK
        string destination
        string address
        string purpose
        datetime tripDate
    }
```

---

## 8. Sequence Diagrams

### 8.1 Profile Setup Flow

```mermaid
sequenceDiagram
    participant User
    participant ProfileSetup
    participant useUserProfile
    participant localStorage
    participant App

    User->>App: Opens application
    App->>useUserProfile: Check isProfileSetup
    useUserProfile->>localStorage: Get profile data
    localStorage-->>useUserProfile: null
    useUserProfile-->>App: isProfileSetup = false
    App->>ProfileSetup: Show 3-step modal

    User->>ProfileSetup: Step 1 — enter name
    User->>ProfileSetup: Step 2 — personal info
    User->>ProfileSetup: Step 3 — address / city / state
    User->>ProfileSetup: Click Complete

    ProfileSetup->>useUserProfile: updateProfile(data)
    useUserProfile->>useUserProfile: Generate ID & timestamps
    useUserProfile->>localStorage: Save profile
    localStorage-->>useUserProfile: Success
    useUserProfile-->>ProfileSetup: Saved
    ProfileSetup->>App: onComplete()
    App->>App: Hide modal; fetch ipify.org → clientIpRef
    App->>App: Show main chat UI
```

### 8.2 Location Resolution Sequence

```mermaid
sequenceDiagram
    participant Browser
    participant FastAPI
    participant CorePy as agent/core.py
    participant Nominatim
    participant Tool
    participant Overpass

    Browser->>FastAPI: WS { user_profile: {city:"Erie", state:"PENNSYLVANIA"}, client_ip:"24.x.x.x" }
    FastAPI->>CorePy: process_request(msg, user_profile, client_ip="24.x.x.x")
    CorePy->>CorePy: location_adapter._client_ip = "24.x.x.x"
    CorePy->>CorePy: _extract_location_from_profile
    CorePy->>CorePy: sleep(1.1s)
    CorePy->>Nominatim: geocode("Erie, PENNSYLVANIA")
    Nominatim-->>CorePy: (42.1292, -80.0851)
    CorePy->>CorePy: context_manager.set_location(lat=42.1292, lon=-80.0851)
    CorePy->>CorePy: Inject "[SYSTEM CONTEXT — User location: Erie, PA]"
    CorePy->>Tool: search_restaurants(query="restaurant")
    Tool->>Tool: _resolve_location → ctx.get_location()
    Tool->>Overpass: query centred on (42.1292, -80.0851)
    Overpass-->>Tool: Restaurants in Erie, PA ✅
    Tool-->>CorePy: { success: true, restaurants: [...] }
    CorePy-->>FastAPI: response message
    FastAPI-->>Browser: { type: "response", message: "..." }
```

### 8.3 Error Handling Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant WebSocket
    participant FastAPI

    User->>Browser: Send message
    Browser->>WebSocket: Send data

    alt Connection OK
        WebSocket->>FastAPI: Forward message
        FastAPI-->>WebSocket: Response
        WebSocket-->>Browser: Display response
    else Connection Lost
        WebSocket->>WebSocket: onerror / onclose
        WebSocket->>Browser: Update status (disconnected)
        Browser->>User: Show "Disconnected" warning
        loop Exponential backoff (max 5 attempts)
            WebSocket->>WebSocket: delay doubles each retry
            WebSocket->>FastAPI: Reconnect attempt
            alt Reconnect Success
                FastAPI-->>WebSocket: Connected
                WebSocket->>Browser: Update status (connected)
                Browser->>User: Show "Reconnected"
            else Still Failing
                WebSocket->>WebSocket: Increment retry count
            end
        end
        WebSocket->>Browser: Max retries — show error
        Browser->>User: Suggest manual refresh
    end
```

### 8.4 Nominatim 429 Retry Sequence

```mermaid
sequenceDiagram
    participant Tool as RestaurantFinder
    participant Nominatim

    Tool->>Tool: attempt 0 — sleep(1.1s)
    Tool->>Nominatim: geocode("Erie, PA")
    Nominatim-->>Tool: HTTP 429

    Tool->>Tool: sleep(2s backoff)
    Tool->>Tool: attempt 1 — sleep(2.2s)
    Tool->>Nominatim: geocode("Erie, PA")
    Nominatim-->>Tool: HTTP 429

    Tool->>Tool: sleep(4s backoff)
    Tool->>Tool: attempt 2 — sleep(3.3s)
    Tool->>Nominatim: geocode("Erie, PA")
    Nominatim-->>Tool: (42.1292, -80.0851) ✅
```

---

## 9. Activity Diagrams

### 9.1 Voice Interaction Flow

```mermaid
flowchart TD
    A[Start] --> B{Interaction Mode?}
    B -->|Push-to-talk| C[User holds mic button]
    B -->|Manual stop| D[User clicks mic]

    C --> E[Microphone activated]
    D --> E

    E --> F[Web Speech API starts recording]
    F --> G[User speaks]
    G --> H{Stop trigger?}

    H -->|Push-to-talk| I[User releases button]
    H -->|Manual| J[User clicks Stop & Send]
    H -->|Auto| K[VOICE_TIMEOUT_MS = 30s elapsed]

    I --> L[Stop recording]
    J --> L
    K --> L

    L --> M[SpeechRecognition transcript]
    M --> N[sendMessage with profile + client_ip]
    N --> O[Backend processes with LangChain agent]
    O --> P[Receive response over WebSocket]
    P --> Q[linkifyText → render <a> tags]
    Q --> R[Display in chat bubble]
    R --> S[Speech Synthesis TTS]
    S --> T[End]

    style A fill:#e1ffe1
    style E fill:#fff4e1
    style O fill:#e1f5ff
    style T fill:#ffe1e1
```

### 9.2 Events Tool Activity

```mermaid
flowchart TD
    A["find_local_events called"] --> B[Get city + state from profile]
    B --> C["_state_to_code('PENNSYLVANIA') → 'PA'"]
    C --> D{Keyword provided?}
    D -->|Yes| E["_keyword_to_segment_id(keyword)\ne.g. 'concert' → KZFzniwnSyZfZ7v7nJ"]
    D -->|No| F[No segment filter]
    E --> G[Build Ticketmaster API URL]
    F --> G
    G --> H["startDateTime = now UTC\nendDateTime = now + 30 days"]
    H --> I["GET /discovery/v2/events\n?countryCode=US&stateCode=PA&city=Erie\n&sort=date,asc&size=20"]
    I --> J{Response OK?}
    J -->|No| K[Return error dict]
    J -->|Yes| L["_parse_events()\nname, date, venue, address\ncategory, price, url\nNO image_url"]
    L --> M["display_limit = max(10, int(limit))\n← floor prevents LLM passing limit=5"]
    M --> N[Return top display_limit events]
    N --> O[LLM formats as markdown links]
    O --> P["linkifyText: [name](url) → <a> tag"]

    style M fill:#fff4e1
    style P fill:#e1ffe1
```

---

## 10. Network Architecture

### 10.1 Communication Protocols

```mermaid
graph LR
    subgraph "Frontend"
        A[React App<br/>:5173]
    end

    subgraph "Backend"
        B[FastAPI<br/>:8000]
    end

    subgraph "External"
        C[OpenRouter<br/>HTTPS]
        D[Open-Meteo<br/>HTTPS]
        E[Overpass API<br/>HTTPS]
        F[Nominatim<br/>HTTPS]
        G[Ticketmaster<br/>HTTPS]
        H[ipify.org<br/>HTTPS — browser]
        I[ipinfo.io<br/>HTTPS — backend]
    end

    A <-->|"WebSocket\nws://localhost:8000/ws/{id}\nPayload: {message, user_profile, client_ip, user_agent}"| B
    B <-->|"HTTPS POST\nAuthorization: Bearer"| C
    B <-->|HTTPS GET| D
    B <-->|HTTPS GET| E
    B <-->|"HTTPS GET\n1 req/sec max"| F
    B <-->|"HTTPS GET\nApikey header"| G
    A <-->|"HTTPS GET\nformat=json"| H
    B <-->|"HTTPS GET\n/client_ip/json"| I

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1e1
```

### 10.2 WebSocket Message Types

```mermaid
flowchart LR
    subgraph "Client → Server"
        A["{ type: 'chat',\n  message: '...',\n  user_profile: {...},\n  client_ip: '24.x.x.x',\n  user_agent: '...',\n  timestamp: ... }"]
    end

    subgraph "Server → Client"
        B["{ type: 'response',\n  message: '...',\n  success: true }"]
        C["{ type: 'action',\n  action: 'save_restaurant',\n  data: { name, address, ... } }"]
        D["{ type: 'error',\n  message: '...' }"]
        E["{ type: 'status',\n  message: 'Processing...' }"]
    end

    A --> B
    A --> C
    A --> D
    A --> E
```

---

## Legend

```mermaid
graph LR
    A[Frontend<br/>Components]
    B[Backend<br/>Services]
    C[External<br/>APIs]
    D[Data<br/>Storage]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1e1
    style D fill:#f0e1ff
```

- **Blue (#e1f5ff)**: Frontend components
- **Yellow (#fff4e1)**: Backend services
- **Red (#ffe1e1)**: External APIs
- **Purple (#f0e1ff)**: Data models / results
- **Green (#e1ffe1)**: Success / correct path
- **Orange (#fff4e1)**: Decision / warning point

---

**Document Version:** 2.0
**Last Updated:** March 2026
**Tools Used:** Mermaid.js

To render these diagrams:

1. Mermaid Live Editor: [mermaid.live](https://mermaid.live)
2. Mermaid extension in VS Code
3. Mermaid plugin in documentation sites (GitBook, Docusaurus, etc.)
