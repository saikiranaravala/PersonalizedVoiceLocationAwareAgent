# System Architecture Diagrams
# Personalized Agentic Voice Assistant

This document contains all Mermaid diagrams for system architecture, data flow, and user journeys.

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Data Flow Diagrams](#2-data-flow-diagrams)
3. [User Journeys](#3-user-journeys)
4. [Component Diagrams](#4-component-diagrams)
5. [Deployment Architecture](#5-deployment-architecture)

---

## 1. System Architecture

### 1.1 High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
        B[React App]
        C[Voice Input]
        D[User Profile<br/>localStorage]
    end
    
    subgraph "Backend Layer"
        E[FastAPI Server]
        F[WebSocket Manager]
        G[LangChain Agent]
        H[Context Manager]
    end
    
    subgraph "Tool Layer"
        I[Weather Tool]
        J[Restaurant Tool]
        K[Uber Tool]
        L[Location Service]
    end
    
    subgraph "External Services"
        M[OpenRouter/OpenAI]
        N[Open-Meteo API]
        O[Zomato API]
        P[Uber Deep Links]
        Q[Nominatim Geocoding]
    end
    
    A --> B
    B --> C
    B <--> D
    B <-->|WebSocket| F
    F <--> E
    E --> G
    G --> H
    G --> I
    G --> J
    G --> K
    I --> L
    J --> L
    K --> L
    G <-->|API Calls| M
    I <--> N
    J <--> O
    K --> P
    L <--> Q
    
    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style E fill:#fff4e1
    style G fill:#f0e1ff
    style M fill:#ffe1e1
```

### 1.2 Component Architecture

```mermaid
graph LR
    subgraph "Frontend Components"
        A[App.tsx]
        B[useVoiceAssistant]
        C[useUserProfile]
        D[WebSocket Client]
        E[ProfileSetup]
        F[ProfileSettings]
    end
    
    subgraph "Backend Components"
        G[api_server.py]
        H[Agent Core]
        I[Tool Base]
        J[Weather Tool]
        K[Zomato Tool]
        L[Uber Tool]
        M[Location Service]
        N[Context Manager]
    end
    
    A --> B
    A --> C
    B --> D
    C --> localStorage
    D <-->|WS| G
    G --> H
    H --> N
    H --> J
    H --> K
    H --> L
    J --> I
    K --> I
    L --> I
    J --> M
    K --> M
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
    
    User->>Browser: Speak/Type message
    Browser->>Browser: Capture input
    Browser->>Browser: Load user_profile from localStorage
    Browser->>WebSocket: {message, user_profile, user_agent}
    WebSocket->>FastAPI: Forward WebSocket message
    FastAPI->>FastAPI: Extract user_profile & user_agent
    FastAPI->>Agent: process_request(msg, profile, agent)
    Agent->>Agent: Store context (profile, agent)
    Agent->>Agent: Understand intent via LLM
    Agent->>Agent: Select appropriate tool
    Agent->>Tool: execute(params, profile, agent)
    Tool->>Tool: Apply smart logic
    Tool->>ExternalAPI: Call API
    ExternalAPI-->>Tool: Return data
    Tool-->>Agent: Formatted result
    Agent-->>FastAPI: Response
    FastAPI-->>WebSocket: {type: "response", message: "..."}
    WebSocket-->>Browser: Deliver response
    Browser->>Browser: Display text
    Browser->>Browser: Speak (TTS)
    Browser->>User: Show & speak result
```

### 2.2 Profile Data Flow

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
    
    D --> I[Pass to useVoiceAssistant hook]
    I --> J[Store in userProfileRef]
    J --> K[User sends message]
    K --> L[Include user_profile in WebSocket]
    L --> M[Backend receives profile]
    M --> N[Agent uses profile for context]
    N --> O[Tools use profile for decisions]
    
    style C fill:#ffe1e1
    style H fill:#e1ffe1
    style M fill:#e1f5ff
```

### 2.3 Uber Smart Pickup Flow

```mermaid
flowchart TD
    A[User: 'Book Uber to mall'] --> B[Backend receives request]
    B --> C[Extract user_agent from message]
    C --> D{Device Type?}
    
    D -->|Mobile<br/>iPhone, Android| E[Use GPS Location]
    D -->|Desktop<br/>Windows, Mac, Linux| F{Profile has address?}
    
    F -->|Yes| G[Build Complete Address]
    F -->|No| H[Use City Location]
    
    G --> I["street + city + state + country<br/>'5013 Burgundy Dr, Erie, PA, USA'"]
    I --> J[Geocode address]
    J --> K[Get coordinates<br/>42.068, -80.123]
    
    E --> L[Get GPS coordinates]
    H --> M[Get city coordinates]
    
    K --> N[Generate Uber URL]
    L --> N
    M --> N
    
    N --> O{URL Structure}
    O --> P["pickup: {<br/>addressLine1: '5013 Burgundy Dr',<br/>addressLine2: 'Erie, PA, USA',<br/>latitude: 42.068,<br/>longitude: -80.123<br/>}"]
    
    P --> Q[Return deep link to user]
    Q --> R[User clicks link]
    R --> S[Uber opens with locations pre-filled]
    
    style D fill:#fff4e1
    style G fill:#e1ffe1
    style P fill:#e1f5ff
    style S fill:#f0e1ff
```

---

## 3. User Journeys

### 3.1 First-Time User Journey

```mermaid
journey
    title First-Time User Experience
    section Arrival
      Open app: 5: User
      See welcome screen: 5: User
    section Profile Setup
      Enter name: 4: User
      Choose gender & age: 4: User
      Enter location: 4: User
      Review profile: 5: User
    section First Interaction
      Click microphone: 5: User
      Ask question: 5: User
      Receive answer: 5: User
      Feel satisfied: 5: User
```

### 3.2 Weather Check Journey

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Listening: Press Space
    Listening --> Processing: "What's the weather?"
    Processing --> FetchingWeather: Agent selects Weather tool
    FetchingWeather --> FormatResponse: Get weather data
    FormatResponse --> Speaking: Generate response
    Speaking --> Idle: Complete
    Idle --> [*]
```

### 3.3 Uber Booking Journey (Desktop)

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Listening: User speaks
    Listening --> Processing: "Book Uber to mall"
    Processing --> CheckDevice: Extract user_agent
    CheckDevice --> CheckProfile: Desktop detected
    CheckProfile --> BuildAddress: Profile has address
    BuildAddress --> Geocode: Combine street+city+state
    Geocode --> GenerateURL: Get coordinates
    GenerateURL --> SendLink: Create deep link
    SendLink --> ClickLink: User clicks
    ClickLink --> UberOpens: Opens Uber app/web
    UberOpens --> PreFilled: Pickup & dropoff filled
    PreFilled --> BookRide: User confirms
    BookRide --> [*]
```

---

## 4. Component Diagrams

### 4.1 Frontend Component Tree

```mermaid
graph TD
    A[App.tsx] --> B[useUserProfile]
    A --> C[useVoiceAssistant]
    A --> D[Theme Selector]
    A --> E[Status Indicator]
    A --> F[Conversation Display]
    A --> G[Voice Visualizer]
    A --> H[Input Area]
    A --> I[ProfileSetup Modal]
    A --> J[ProfileSettings Modal]
    
    B --> K[localStorage]
    C --> L[WebSocket Client]
    I --> M[Step 1: Name]
    I --> N[Step 2: Personal]
    I --> O[Step 3: Location]
    J --> P[Basic Info Section]
    J --> Q[Location Section]
    J --> R[Danger Zone]
    
    style A fill:#e1f5ff
    style B fill:#ffe1e1
    style C fill:#ffe1e1
    style I fill:#f0e1ff
    style J fill:#f0e1ff
```

### 4.2 Backend Tool Architecture

```mermaid
classDiagram
    class BaseTool {
        +name: str
        +description: str
        +execute(**kwargs) Dict
        +validate_inputs(**kwargs) bool
    }
    
    class WeatherTool {
        -location_service: LocationService
        +execute(location: str) Dict
        -_fetch_weather(lat, lon) Dict
    }
    
    class ZomatoTool {
        -api_key: str
        -location_service: LocationService
        +execute(cuisine: str, location: str) Dict
        -_search_restaurants(params) List
    }
    
    class UberTool {
        -location_service: LocationService
        +execute(destination: str, pickup: str,<br/>user_agent: str, user_profile: dict) Dict
        -_build_complete_address(profile) str
        -_generate_deep_link(pickup, dropoff) str
    }
    
    class LocationService {
        -geocoder: Nominatim
        -cache: Dict
        +get_current_location() Dict
        +geocode_address(address: str) Tuple
        +reverse_geocode(lat, lon) str
    }
    
    BaseTool <|-- WeatherTool
    BaseTool <|-- ZomatoTool
    BaseTool <|-- UberTool
    WeatherTool --> LocationService
    ZomatoTool --> LocationService
    UberTool --> LocationService
```

### 4.3 Agent Decision Flow

```mermaid
flowchart TD
    A[User Message Received] --> B[LLM Processes Message]
    B --> C{Intent Detection}
    
    C -->|Weather query| D[Weather Tool]
    C -->|Restaurant query| E[Zomato Tool]
    C -->|Ride query| F[Uber Tool]
    C -->|General question| G[Direct LLM Response]
    
    D --> H[Get location]
    E --> H
    F --> H
    
    H --> I[Location Service]
    I --> J{GPS Available?}
    J -->|Yes| K[Use GPS]
    J -->|No| L[Use Profile/Default]
    
    K --> M[Execute Tool]
    L --> M
    
    M --> N[Format Response]
    G --> N
    
    N --> O[Return to User]
    
    style C fill:#fff4e1
    style M fill:#e1ffe1
    style O fill:#e1f5ff
```

---

## 5. Deployment Architecture

### 5.1 Development Environment

```mermaid
graph LR
    subgraph "Developer Machine"
        A[VS Code]
        B[Terminal 1<br/>Backend]
        C[Terminal 2<br/>Frontend]
    end
    
    subgraph "Local Services"
        D[FastAPI<br/>:8000]
        E[Vite Dev Server<br/>:5173]
        F[Browser<br/>localhost:5173]
    end
    
    subgraph "External APIs"
        G[OpenRouter]
        H[Open-Meteo]
        I[Zomato]
        J[Nominatim]
    end
    
    A --> B
    A --> C
    B --> D
    C --> E
    E --> F
    F <-->|WebSocket| D
    D <--> G
    D <--> H
    D <--> I
    D <--> J
```

### 5.2 Production Deployment (Future)

```mermaid
graph TB
    subgraph "CDN"
        A[CloudFlare]
        B[Static Assets<br/>JS, CSS, Images]
    end
    
    subgraph "Load Balancer"
        C[NGINX]
    end
    
    subgraph "Backend Cluster"
        D[FastAPI Instance 1]
        E[FastAPI Instance 2]
        F[FastAPI Instance N]
    end
    
    subgraph "Data Layer"
        G[Redis<br/>Session Store]
        H[PostgreSQL<br/>Analytics]
    end
    
    subgraph "Monitoring"
        I[LangSmith]
        J[Prometheus]
        K[Grafana]
    end
    
    Users --> A
    A --> C
    C --> D
    C --> E
    C --> F
    D --> G
    E --> G
    F --> G
    D --> H
    E --> H
    F --> H
    D --> I
    D --> J
    J --> K
```

### 5.3 Data Flow in Production

```mermaid
flowchart LR
    A[User Browser] -->|HTTPS/WSS| B[CloudFlare CDN]
    B -->|SSL Termination| C[NGINX Load Balancer]
    C -->|Round Robin| D[FastAPI Pod 1]
    C -->|Round Robin| E[FastAPI Pod 2]
    D <-->|Session| F[Redis Cluster]
    E <-->|Session| F
    D -->|Logs| G[LangSmith]
    E -->|Logs| G
    D -->|Metrics| H[Prometheus]
    E -->|Metrics| H
    H --> I[Grafana Dashboard]
    
    style A fill:#e1f5ff
    style D fill:#fff4e1
    style E fill:#fff4e1
    style F fill:#ffe1e1
    style I fill:#f0e1ff
```

---

## 6. State Diagrams

### 6.1 Application State

```mermaid
stateDiagram-v2
    [*] --> Loading
    Loading --> ProfileSetup: No profile
    Loading --> Connected: Has profile
    
    ProfileSetup --> Step1
    Step1 --> Step2: Next
    Step2 --> Step3: Next
    Step3 --> ProfileComplete: Complete
    ProfileComplete --> Connected
    
    Connected --> Idle
    Idle --> Listening: User activates voice
    Listening --> Processing: Speech detected
    Processing --> Idle: Response received
    
    Idle --> Error: Connection lost
    Error --> Reconnecting: Auto retry
    Reconnecting --> Connected: Success
    Reconnecting --> Error: Failed
    
    Connected --> [*]: User closes
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
    Failed --> Reconnecting: Auto retry (1s delay)
    Reconnecting --> Connecting: Attempt reconnect
    Reconnecting --> Disconnected: Max retries (5)
    Connected --> [*]: User closes app
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
    localStorage-->>useUserProfile: null (no data)
    useUserProfile-->>App: isProfileSetup = false
    App->>ProfileSetup: Show modal
    
    User->>ProfileSetup: Enter name
    User->>ProfileSetup: Enter details
    User->>ProfileSetup: Enter location
    User->>ProfileSetup: Click Complete
    
    ProfileSetup->>useUserProfile: updateProfile(data)
    useUserProfile->>useUserProfile: Generate ID & timestamps
    useUserProfile->>localStorage: Save data
    localStorage-->>useUserProfile: Success
    useUserProfile-->>ProfileSetup: Profile saved
    ProfileSetup->>App: onComplete()
    App->>App: Hide modal, show main UI
```

### 8.2 Error Handling Flow

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
        WebSocket->>WebSocket: onclose event
        WebSocket->>Browser: Update status (disconnected)
        Browser->>User: Show "Disconnected" warning
        WebSocket->>WebSocket: Auto-reconnect (attempt 1)
        
        alt Reconnect Success
            WebSocket->>FastAPI: Reconnect
            FastAPI-->>WebSocket: Connected
            WebSocket->>Browser: Update status (connected)
            Browser->>User: Show "Reconnected" message
        else Reconnect Failed (Max retries)
            WebSocket->>Browser: Update status (error)
            Browser->>User: Show error message
            Browser->>User: Suggest manual refresh
        end
    end
```

---

## 9. Activity Diagrams

### 9.1 Voice Interaction Flow

```mermaid
flowchart TD
    A[Start] --> B{Push-to-Talk or Continuous?}
    B -->|Push-to-Talk| C[User holds Space bar]
    B -->|Continuous| D[User clicks microphone]
    
    C --> E[Microphone activated]
    D --> E
    
    E --> F[Start recording]
    F --> G[User speaks]
    G --> H{User stopped speaking?}
    
    H -->|Push-to-Talk| I[User releases Space]
    H -->|Continuous| J[3s silence detected]
    
    I --> K[Stop recording]
    J --> K
    
    K --> L[Convert speech to text]
    L --> M[Send to backend]
    M --> N[Process with AI]
    N --> O[Receive response]
    O --> P[Display text]
    P --> Q[Speak response TTS]
    Q --> R[End]
    
    style A fill:#e1ffe1
    style E fill:#fff4e1
    style N fill:#e1f5ff
    style R fill:#ffe1e1
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
        E[Zomato<br/>HTTPS]
        F[Nominatim<br/>HTTPS]
    end
    
    A <-->|WebSocket<br/>ws://localhost:8000/ws/{id}| B
    B <-->|HTTPS POST<br/>Authorization: Bearer| C
    B <-->|HTTPS GET| D
    B <-->|HTTPS GET<br/>user-key header| E
    B <-->|HTTPS GET| F
    
    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1e1
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
- **Red (#ffe1e1)**: External APIs / Data storage
- **Purple (#f0e1ff)**: Data models / Results

---

**Document Version:** 1.0.0  
**Last Updated:** March 7, 2026  
**Tools Used:** Mermaid.js

To render these diagrams:
1. Use Mermaid Live Editor: https://mermaid.live
2. Use Mermaid extension in VS Code
3. Use Mermaid plugin in documentation sites (GitBook, Docusaurus, etc.)
