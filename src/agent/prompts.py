"""System prompts and templates for the agent."""

SYSTEM_PROMPT = """You are a helpful, voice-first AI assistant that acts as a digital concierge. Your role is to understand natural language commands and help users with real-world tasks.

Key Capabilities:
- Get weather information for any location
- Search for nearby restaurants based on cuisine preferences
- Generate Uber ride booking links
- Understand and maintain conversation context
- Use the user's current GPS location when relevant

Guidelines:
1. Be conversational and natural in your responses
2. When location isn't specified, assume the user means their current location
3. Always confirm important details before taking actions
4. Provide clear, concise responses suitable for voice output
5. If you need to use a tool, explain what you're doing
6. Handle errors gracefully and offer alternatives

Output Formatting Rules (follow these strictly regardless of the LLM model):
- Do NOT use emojis anywhere in responses
- Do NOT use bold markdown (**text**) or italic markdown (*text*)
- For lists of items (events, restaurants, etc.), use plain numbered format: "1. Name at Venue on Date."
- For URLs, always use markdown link format: [Event Name](https://url.com) — never bare URLs
- Keep responses concise — one sentence per item in a list
- Do not add section headers or category labels (no "Sports Events:", "Comedy Shows:" etc.)
- Do not editorialize (no "exciting", "hilarious", "world-famous") — just state the facts

Context Information:
{context}

Remember: You can access the user's current location and should use it to provide contextual, location-aware responses.
"""
#ToDo: Add user greeting to line 27

USER_GREETING = """Hello! I'm your personalized AI assistant. I can help you with:
- Booking rides with Uber
- Finding restaurants nearby
- Checking the weather
- And much more!

What would you like help with today?"""

TOOL_EXECUTION_PREFIX = "Let me help you with that. "

TOOL_ERROR_RESPONSE = "I encountered an issue: {error}. Let me try a different approach."

FALLBACK_RESPONSE = "I'm not sure I understood that correctly. Could you please rephrase your request?"

CONFIRMATION_PROMPT = "Just to confirm, you want me to {action}. Is that correct?"

COMPLETION_RESPONSE = "Done! {details}"


def format_system_prompt(context: str) -> str:
    """Format the system prompt with context.
    
    Args:
        context: Context information string
        
    Returns:
        Formatted system prompt
    """
    return SYSTEM_PROMPT.format(context=context)


def format_tool_response(tool_name: str, result: dict) -> str:
    """Format a tool execution result into a natural response.
    
    Args:
        tool_name: Name of the tool that was executed
        result: Tool execution result dictionary
        
    Returns:
        Natural language response string
    """
    if not result.get("success"):
        error = result.get("error", "Unknown error")
        return TOOL_ERROR_RESPONSE.format(error=error)
    
    # Tool-specific formatting
    if tool_name == "get_weather":
        return result.get("summary", "Weather information retrieved.")
    
    elif tool_name == "search_restaurants":
        restaurants = result.get("restaurants", [])
        if not restaurants:
            return "I couldn't find any restaurants matching your criteria."
        
        response = f"I found {len(restaurants)} great options:\n"
        for i, resto in enumerate(restaurants[:3], 1):
            response += f"{i}. {resto['name']} - {resto['cuisine']} (Rating: {resto.get('rating', 'N/A')})\n"
        
        if len(restaurants) > 3:
            response += f"...and {len(restaurants) - 3} more options."
        
        return response
    
    elif tool_name == "book_uber_ride":
        return f"{result.get('message', 'Uber link generated.')} {result.get('instructions', '')}"
    
    # Default response
    return result.get("message", "Task completed successfully.")


def format_restaurant_selection(restaurants: list) -> str:
    """Format restaurant list for voice output.
    
    Args:
        restaurants: List of restaurant dictionaries
        
    Returns:
        Formatted string for speech
    """
    if not restaurants:
        return "No restaurants found."
    
    response = f"I found {len(restaurants)} restaurants. Here are the top options: "
    
    for i, resto in enumerate(restaurants[:3], 1):
        name = resto.get('name', 'Unknown')
        rating = resto.get('rating', 'N/A')
        cuisine = resto.get('cuisine', '')
        
        response += f"Option {i}: {name}"
        if cuisine:
            response += f", serving {cuisine}"
        if rating != 'N/A':
            response += f", rated {rating} stars"
        response += ". "
    
    return response
