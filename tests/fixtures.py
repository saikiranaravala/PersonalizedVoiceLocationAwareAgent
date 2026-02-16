"""Pytest fixtures and test utilities."""

import pytest
from unittest.mock import Mock, MagicMock

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.location import LocationService
from services.context import ContextManager
from tools.weather import WeatherTool
from tools.uber import UberTool
from tools.zomato import ZomatoTool


@pytest.fixture
def mock_location_service():
    """Create a mock location service."""
    service = Mock(spec=LocationService)
    
    # Mock GPS location
    service.get_current_location.return_value = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "New York, NY, USA",
        "city": "New York",
        "country": "USA",
    }
    
    # Mock geocoding
    service.geocode_address.return_value = (40.7580, -73.9855)  # Times Square
    
    # Mock reverse geocoding
    service.reverse_geocode.return_value = "Times Square, Manhattan, NY"
    
    # Mock distance calculation
    service.get_distance.return_value = 2.5
    
    return service


@pytest.fixture
def mock_context_manager():
    """Create a mock context manager."""
    manager = Mock(spec=ContextManager)
    
    manager.preferences = {}
    manager.conversation_history = []
    manager.current_location = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "New York, NY",
    }
    
    manager.get_context_summary.return_value = "Current location: New York, NY"
    
    return manager


@pytest.fixture
def weather_tool(mock_location_service):
    """Create a weather tool instance."""
    return WeatherTool(mock_location_service)


@pytest.fixture
def uber_tool(mock_location_service):
    """Create an Uber tool instance."""
    return UberTool(mock_location_service)


@pytest.fixture
def zomato_tool(mock_location_service):
    """Create a Zomato tool instance."""
    return ZomatoTool(mock_location_service)


@pytest.fixture
def sample_weather_response():
    """Sample weather API response."""
    return {
        "current_weather": {
            "temperature": 72,
            "weathercode": 0,
            "windspeed": 10.5,
            "time": "2024-01-15T12:00:00"
        }
    }


@pytest.fixture
def sample_restaurants():
    """Sample restaurant data."""
    return [
        {
            "name": "Bella Italia",
            "cuisine": "Italian",
            "rating": 4.5,
            "address": "123 Main St, New York, NY",
            "price_range": 3,
        },
        {
            "name": "Pasta Paradise",
            "cuisine": "Italian",
            "rating": 4.3,
            "address": "456 Oak Ave, New York, NY",
            "price_range": 2,
        },
        {
            "name": "Trattoria Roma",
            "cuisine": "Italian",
            "rating": 4.7,
            "address": "789 Elm St, New York, NY",
            "price_range": 4,
        },
    ]


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    response = Mock()
    response.choices = [
        Mock(message=Mock(content="I can help you with that!"))
    ]
    return response
