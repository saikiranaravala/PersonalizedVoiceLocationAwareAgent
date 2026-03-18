"""Core agent orchestrator with LangChain integration."""

import os
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool

from agent.prompts import (
    format_system_prompt,
    format_tool_response,
    USER_GREETING,
)
from services.context import ContextManager
from services.location import LocationService
from tools.uber import UberTool
from tools.weather import WeatherTool
from tools.restaurant_finder import RestaurantFinder
from tools.save_preferences_tool import SaveRestaurantTool, SaveUberTripTool

from utils.config import config
from utils.logger import logger


def create_openrouter_llm(model_name: str, temperature: float, api_key: str, base_url: str = None):
    """Create a ChatOpenAI instance configured for OpenRouter.
    
    Args:
        model_name: Model name (e.g., 'anthropic/claude-3-sonnet', 'openai/gpt-4')
        temperature: Temperature setting
        api_key: OpenRouter API key
        base_url: Optional custom base URL (defaults to OpenRouter)
        
    Returns:
        ChatOpenAI instance configured for OpenRouter
    """
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        openai_api_key=api_key,
        openai_api_base=base_url or "https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/personalized-agentic-assistant",
            "X-Title": "Personalized Agentic Assistant"
        }
    )


class LocationContextAdapter:
    """Adapter that wraps ContextManager to look like a LocationService.

    Tools call get_current_location() expecting lat/lon from the server.
    This adapter intercepts that call and returns the user-profile location
    stored in ContextManager instead, falling back to real LocationService
    only when no profile location is available.
    """

    def __init__(self, context_manager: "ContextManager", fallback_service: "LocationService"):
        self._ctx = context_manager
        self._fallback = fallback_service

    # Called by RestaurantFinder._coords_from_service (ContextManager path)
    def get_location(self):
        return self._ctx.get_location()

    # Called by WeatherTool, UberTool, and RestaurantFinder._coords_from_service (LocationService path)
    def get_current_location(self):
        loc = self._ctx.get_location()
        if loc and (loc.get("latitude") or loc.get("city")):
            # Return context location — has user profile data
            return loc
        # Fallback to real GPS/IP detection
        return self._fallback.get_current_location()

    # Proxy any other LocationService methods tools might call
    def geocode_address(self, address: str):
        return self._fallback.geocode_address(address)

    def reverse_geocode(self, latitude: float, longitude: float):
        return self._fallback.reverse_geocode(latitude, longitude)

    def get_distance(self, lat1, lon1, lat2, lon2):
        return self._fallback.get_distance(lat1, lon1, lat2, lon2)


class AgenticAssistant:
    """Main agentic assistant orchestrator."""

    def __init__(self):
        """Initialize the agentic assistant."""
        logger.info("Initializing Agentic Assistant...")
        
        # Initialize services
        self.location_service = LocationService()
        self.context_manager = ContextManager()

        # Get current location and set as initial context
        current_location = self.location_service.get_current_location()
        self.context_manager.set_location(current_location)

        # Adapter: gives all tools a single location_service interface
        # that returns user-profile location when available, server IP otherwise
        self.location_adapter = LocationContextAdapter(
            self.context_manager, self.location_service
        )

        # WebSocket sender — injected per-request via set_websocket_sender().
        # SaveRestaurantTool and SaveUberTripTool use this to push action
        # messages back to the frontend so it can persist to localStorage.
        self._ws_sender = None
        
        # Initialize tools FIRST (before LLM)
        self.tools = self._initialize_tools()
        
        # Initialize LLM (can now bind tools if needed)
        self.llm = self._initialize_llm()
        
        # Initialize agent
        self.agent_executor = self._initialize_agent()
        
        logger.info("Agentic Assistant initialized successfully")

    def _initialize_tools(self) -> List[StructuredTool]:
        """Initialize all available tools.
        
        Returns:
            List of LangChain tools
        """
        tools = []
        
        # Weather tool
        weather_tool = WeatherTool(self.location_adapter)
        tools.append(
            StructuredTool.from_function(
                func=weather_tool.execute,
                name=weather_tool.name,
                description=weather_tool.description,
            )
        )
        
        # Restaurant search tool
        restaurant_tool = RestaurantFinder(self.location_adapter)
        tools.append(
            StructuredTool.from_function(
                func=restaurant_tool.execute,
                name=restaurant_tool.name,
                description=restaurant_tool.description,
            )
        )
        
        # Uber booking tool
        self.uber_tool = UberTool(self.location_adapter)
        
        # Create wrapper that adds context (user_agent, user_profile)
        def uber_execute_with_context(destination: str, pickup: str = None, **kwargs):
            """Wrapper that adds request context to Uber tool."""
            # Get context from current request (will be set in process_request)
            user_agent = getattr(self, '_current_user_agent', None)
            user_profile = getattr(self, '_current_user_profile', None)
            
            return self.uber_tool.execute(
                destination=destination,
                pickup=pickup,
                user_agent=user_agent,
                user_profile=user_profile,
                **kwargs
            )
        
        tools.append(
            StructuredTool.from_function(
                func=uber_execute_with_context,
                name=self.uber_tool.name,
                description=self.uber_tool.description,
            )
        )
        
        # Save Restaurant tool — persists favorite restaurants to frontend localStorage
        # websocket_sender is None at init; injected per-request via set_websocket_sender()
        self.save_restaurant_tool = SaveRestaurantTool()
        tools.append(
            StructuredTool.from_function(
                func=self.save_restaurant_tool.execute,
                name=self.save_restaurant_tool.name,
                description=self.save_restaurant_tool.description,
            )
        )

        # Save Uber Trip tool — persists trip history to frontend localStorage
        self.save_uber_trip_tool = SaveUberTripTool()
        tools.append(
            StructuredTool.from_function(
                func=self.save_uber_trip_tool.execute,
                name=self.save_uber_trip_tool.name,
                description=self.save_uber_trip_tool.description,
            )
        )

        logger.info(f"Initialized {len(tools)} tools")
        return tools

    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model.
        
        Returns:
            ChatOpenAI instance
        """
        # Configure LangSmith if enabled
        if config.langsmith_enabled:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = config.langsmith_api_key
            os.environ["LANGCHAIN_PROJECT"] = config.get(
                "monitoring.langsmith_project", 
                "personalized-agentic-assistant"
            )
            logger.info("LangSmith tracing enabled")
        
        model_name = config.get("agent.model", "gpt-4")
        temperature = config.get("agent.temperature", 0.7)
        use_openrouter = config.get("agent.use_openrouter", False)
        
        if use_openrouter:
            # Use OpenRouter
            api_key = config.get_env("OPENROUTER_API_KEY") or config.openai_api_key
            base_url = config.get("agent.openrouter_base_url")
            
            llm = create_openrouter_llm(
                model_name=model_name,
                temperature=temperature,
                api_key=api_key,
                base_url=base_url
            )
            logger.info(f"Initialized LLM via OpenRouter: {model_name}")
        else:
            # Use OpenAI directly
            llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                openai_api_key=config.openai_api_key,
            )
            logger.info(f"Initialized LLM via OpenAI: {model_name}")
        
        # Bind tools to LLM if it supports tool calling
        try:
            # This ensures the LLM knows about available tools
            llm = llm.bind_tools(self.tools) if hasattr(self, 'tools') and self.tools else llm
            logger.info("Tools bound to LLM successfully")
        except Exception as e:
            logger.warning(f"Could not bind tools to LLM: {e}. Continuing without tool binding.")
        
        return llm

    def _initialize_agent(self) -> AgentExecutor:
        """Initialize the agent executor.
        
        Returns:
            AgentExecutor instance
        """
        # Create prompt template
        context = self.context_manager.get_context_summary()
        system_prompt = format_system_prompt(context)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent using tool calling (not deprecated functions)
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=config.get("agent.max_iterations", 10),
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )
        
        logger.info("Agent executor initialized")
        return agent_executor

    def set_websocket_sender(self, sender) -> None:
        """Inject the WebSocket send function for the current request.

        Must be called once per WebSocket connection (or per request) so that
        SaveRestaurantTool and SaveUberTripTool can push `action` messages back
        to the frontend, which then persists data to browser localStorage.

        Args:
            sender: Callable that accepts a JSON string and sends it over WS.
                    Pass None to clear (e.g. when a connection closes).

        Example (FastAPI):
            def ws_send(msg: str):
                asyncio.create_task(websocket.send_text(msg))
            assistant.set_websocket_sender(ws_send)
        """
        self._ws_sender = sender
        self.save_restaurant_tool.websocket_sender = sender
        self.save_uber_trip_tool.websocket_sender = sender
        logger.debug(f"WebSocket sender {'set' if sender else 'cleared'}")


    def _extract_location_from_profile(self, user_profile: dict) -> Optional[Dict[str, Any]]:
        """Extract and geocode location from the frontend user_profile payload.

        Reads city/state/address from the React frontend profile (camelCase keys),
        geocodes to real lat/lon via Nominatim so ALL tools get accurate coordinates,
        then returns a dict compatible with ContextManager.set_location().
        Returns None if the profile has no usable location data.
        """
        if not user_profile or not isinstance(user_profile, dict):
            return None

        city    = user_profile.get('city')    or user_profile.get('City',    '')
        state   = user_profile.get('state')   or user_profile.get('State',   '')
        country = user_profile.get('country') or user_profile.get('Country') or 'US'
        address = user_profile.get('address') or user_profile.get('Address', '')

        if not city and not address:
            return None

        # Build a human-readable address string
        parts = [p for p in [address, city, state, country] if p]
        full_address = ', '.join(parts)

        # Geocode city+state to real lat/lon so tools get accurate coordinates
        # Use "city, state" as it geocodes more reliably than a street address
        geocode_query = f"{city}, {state}" if city and state else city or address
        latitude, longitude = None, None
        try:
            from tools.restaurant_finder import RestaurantFinder
            lat, lon = RestaurantFinder._geocode_city(geocode_query)
            latitude, longitude = lat, lon
            logger.info(
                f"Geocoded user profile location '{geocode_query}' "
                f"→ ({latitude:.4f}, {longitude:.4f})"
            )
        except Exception as e:
            logger.warning(
                f"Could not geocode profile location '{geocode_query}': {e}. "
                f"Tools will geocode on demand."
            )

        return {
            'address':   full_address,
            'city':      city,
            'state':     state,
            'country':   country,
            'latitude':  latitude,
            'longitude': longitude,
            'source':    'user_profile',
        }

    def process_request(self, user_input: str, user_agent: str = None, 
                       user_profile: dict = None) -> Dict[str, Any]:
        """Process a user request with context.
        
        Args:
            user_input: User's input text
            user_agent: HTTP User-Agent header for device detection
            user_profile: User profile data (name, address, preferences, etc.)
            
        Returns:
            Response dictionary with output and metadata
        """
        logger.info(f"Processing request: {user_input}")
        
        # Store context for tool wrappers to access
        self._current_user_agent = user_agent
        self._current_user_profile = user_profile
        
        # Add to conversation history
        self.context_manager.add_to_history("user", user_input)
        
        try:
            # Resolve location: user profile takes priority over server IP.
            # Frontend sends user_profile with city/state from localStorage.
            location_from_profile = self._extract_location_from_profile(user_profile)

            if location_from_profile:
                self.context_manager.set_location(location_from_profile)
                logger.info(
                    f"Using user profile location: "
                    f"{location_from_profile.get('address', 'unknown')}"
                )
            else:
                current_location = self.location_service.get_current_location()
                self.context_manager.set_location(current_location)
                logger.info('No profile location — using server IP location')
            
            # Get conversation history for context
            history = self.context_manager.get_history(limit=5)
            chat_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in history[:-1]  # Exclude current message
            ]
            
            # Execute agent
            # Inject current location directly into the user message so the LLM
            # always uses the right location — works regardless of LangChain internals.
            location = self.context_manager.get_location()
            location_hint = ""
            if location:
                city    = location.get("city", "")
                state   = location.get("state", "")
                address = location.get("address", "")
                loc_str = f"{city}, {state}" if city and state else address
                if loc_str:
                    location_hint = (
                        f"[SYSTEM CONTEXT - User location: {loc_str}. "
                        "Always use this location for weather, restaurants, and ride queries "
                        "unless the user explicitly specifies a different place.]\n\n"
                    )

            result = self.agent_executor.invoke({
                "input": location_hint + user_input,
                "chat_history": chat_history,
            })
            
            output = result.get("output", "I'm not sure how to help with that.")
            
            # Add response to history
            self.context_manager.add_to_history("assistant", output)
            
            # Extract preferences if any
            self.context_manager.extract_preferences_from_interaction(
                user_input, output
            )
            
            response = {
                "success": True,
                "output": output,
                "intermediate_steps": result.get("intermediate_steps", []),
            }
            
            logger.info(f"Request processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            error_response = (
                "I apologize, but I encountered an error processing your request. "
                "Could you please try rephrasing it?"
            )
            
            self.context_manager.add_to_history("assistant", error_response)
            
            return {
                "success": False,
                "output": error_response,
                "error": str(e),
            }

    def get_greeting(self) -> str:
        """Get greeting message.
        
        Returns:
            Greeting string
        """
        return USER_GREETING

    def reset_conversation(self):
        """Reset conversation history and context."""
        self.context_manager.clear_history()
        logger.info("Conversation reset")

    def get_context_summary(self) -> str:
        """Get current context summary.
        
        Returns:
            Context summary string
        """
        return self.context_manager.get_context_summary()
