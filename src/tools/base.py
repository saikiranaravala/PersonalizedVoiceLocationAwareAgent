"""Base tool interface for the agentic system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from utils.logger import logger


class BaseTool(ABC):
    """Abstract base class for all tools."""

    name: str = "base_tool"
    description: str = "Base tool description"
    
    def __init__(self):
        """Initialize the tool."""
        logger.debug(f"Initialized tool: {self.name}")
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool's main functionality.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            Dictionary with execution results
        """
        pass
    
    def validate_inputs(self, **kwargs) -> bool:
        """Validate tool inputs before execution.
        
        Args:
            **kwargs: Tool inputs to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle execution errors.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Error response dictionary
        """
        logger.error(f"Error in {self.name}: {str(error)}")
        return {
            "success": False,
            "error": str(error),
            "tool": self.name
        }
    
    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Make the tool callable.
        
        Args:
            **kwargs: Tool arguments
            
        Returns:
            Execution results
        """
        try:
            if not self.validate_inputs(**kwargs):
                return {
                    "success": False,
                    "error": "Invalid inputs",
                    "tool": self.name
                }
            
            logger.info(f"Executing tool: {self.name}")
            result = self.execute(**kwargs)
            
            if result is None:
                result = {"success": True, "tool": self.name}
            elif isinstance(result, dict):
                result.setdefault("success", True)
                result.setdefault("tool", self.name)
            
            return result
            
        except Exception as e:
            return self.handle_error(e)
    
    def to_langchain_tool(self):
        """Convert to LangChain tool format.
        
        Returns:
            LangChain tool dictionary
        """
        from langchain.tools import StructuredTool
        
        return StructuredTool.from_function(
            func=self.execute,
            name=self.name,
            description=self.description,
        )
