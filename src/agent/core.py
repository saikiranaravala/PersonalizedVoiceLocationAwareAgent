"""Core agent orchestrator with LangChain integration."""

import os
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_openai_functions_agent
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
from tools.zomato import ZomatoTool
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


class AgenticAssistant:
    """Main agentic assistant orchestrator."""

    def __init__(self):
        """Initialize the agentic assistant."""
        logger.info("Initializing Agentic Assistant...")
        
        # Initialize services
        self.location_service = LocationService()
        self.context_manager = ContextManager()
        
        # Get current location and set context
        current_location = self.location_service.get_current_location()
        self.context_manager.set_location(current_location)
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        # Initialize LLM
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
        weather_tool = WeatherTool(self.location_service)
        tools.append(
            StructuredTool.from_function(
                func=weather_tool.execute,
                name=weather_tool.name,
                description=weather_tool.description,
            )
        )
        
        # Restaurant search tool
        zomato_tool = ZomatoTool(self.location_service)
        tools.append(
            StructuredTool.from_function(
                func=zomato_tool.execute,
                name=zomato_tool.name,
                description=zomato_tool.description,
            )
        )
        
        # Uber booking tool
        uber_tool = UberTool(self.location_service)
        tools.append(
            StructuredTool.from_function(
                func=uber_tool.execute,
                name=uber_tool.name,
                description=uber_tool.description,
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
        
        # Create agent
        agent = create_openai_functions_agent(
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

    def process_request(self, user_input: str) -> Dict[str, Any]:
        """Process a user request.
        
        Args:
            user_input: User's input text
            
        Returns:
            Response dictionary with output and metadata
        """
        logger.info(f"Processing request: {user_input}")
        
        # Add to conversation history
        self.context_manager.add_to_history("user", user_input)
        
        try:
            # Update context with latest location
            current_location = self.location_service.get_current_location()
            self.context_manager.set_location(current_location)
            
            # Get conversation history for context
            history = self.context_manager.get_history(limit=5)
            chat_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in history[:-1]  # Exclude current message
            ]
            
            # Execute agent
            result = self.agent_executor.invoke({
                "input": user_input,
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
