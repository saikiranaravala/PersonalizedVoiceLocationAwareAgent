"""User context and preference management."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.config import config
from utils.logger import logger


class ContextManager:
    """Manages user context, preferences, and conversation history."""

    def __init__(self):
        """Initialize context manager."""
        self.persist_preferences = config.get("user_context.persist_preferences", True)
        self.preferences_file = Path(config.get("user_context.preferences_file", "data/user_preferences.json"))
        self.history_limit = config.get("user_context.history_limit", 100)
        
        self.preferences = {}
        self.conversation_history = []
        self.current_location = None
        
        if self.persist_preferences:
            self._load_preferences()

    def _load_preferences(self):
        """Load user preferences from file."""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r') as f:
                    self.preferences = json.load(f)
                logger.info(f"Loaded user preferences from {self.preferences_file}")
            else:
                logger.info("No existing preferences file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")
            self.preferences = {}

    def _save_preferences(self):
        """Save user preferences to file."""
        if not self.persist_preferences:
            return
            
        try:
            self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
            logger.debug("Saved user preferences")
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")

    def set_preference(self, key: str, value: Any):
        """Set a user preference.

        Args:
            key: Preference key
            value: Preference value
        """
        self.preferences[key] = value
        self._save_preferences()
        logger.info(f"Set preference: {key} = {value}")

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference.

        Args:
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value or default
        """
        return self.preferences.get(key, default)

    def add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add an entry to conversation history.

        Args:
            role: Speaker role ('user' or 'assistant')
            content: Message content
            metadata: Optional metadata dictionary
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        self.conversation_history.append(entry)
        
        # Trim history if exceeds limit
        if len(self.conversation_history) > self.history_limit:
            self.conversation_history = self.conversation_history[-self.history_limit:]
        
        logger.debug(f"Added to history: {role} - {content[:50]}...")

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history.

        Args:
            limit: Maximum number of entries to return (most recent)

        Returns:
            List of history entries
        """
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Cleared conversation history")

    def set_location(self, location: Dict[str, Any]):
        """Set current location context.

        Args:
            location: Location dictionary with lat, lng, address
        """
        self.current_location = location
        logger.info(f"Updated location context: {location.get('address', 'Unknown')}")

    def get_location(self) -> Optional[Dict[str, Any]]:
        """Get current location context.

        Returns:
            Location dictionary or None
        """
        return self.current_location

    def get_context_summary(self) -> str:
        """Get a summary of current context for the LLM.

        Returns:
            Context summary string
        """
        summary_parts = []
        
        # Location context
        if self.current_location:
            location_str = self.current_location.get('address', 'Unknown location')
            summary_parts.append(f"Current location: {location_str}")
        
        # Key preferences
        if self.preferences:
            pref_items = []
            for key, value in list(self.preferences.items())[:5]:
                pref_items.append(f"{key}: {value}")
            if pref_items:
                summary_parts.append("User preferences: " + ", ".join(pref_items))
        
        # Recent history context
        recent_history = self.get_history(limit=5)
        if recent_history:
            summary_parts.append(f"Recent conversation: {len(recent_history)} messages")
        
        return "\n".join(summary_parts) if summary_parts else "No context available"

    def extract_preferences_from_interaction(self, user_input: str, agent_response: str):
        """Attempt to extract and store preferences from conversation.

        Args:
            user_input: User's message
            agent_response: Agent's response
        """
        # Simple keyword-based preference extraction
        # In production, this would use the LLM for better extraction
        
        keywords = {
            "favorite": "favorite",
            "prefer": "preference",
            "like": "like",
            "love": "love",
            "hate": "dislike",
        }
        
        for keyword, pref_type in keywords.items():
            if keyword in user_input.lower():
                # Store as a preference (simplified)
                pref_key = f"{pref_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.set_preference(pref_key, user_input)
                logger.debug(f"Extracted potential preference: {pref_key}")
