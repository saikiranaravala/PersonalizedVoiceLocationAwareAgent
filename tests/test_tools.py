"""Unit tests for tools."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from fixtures import (
    mock_location_service,
    weather_tool,
    uber_tool,
    zomato_tool,
    sample_weather_response,
    sample_restaurants,
)


class TestWeatherTool:
    """Test cases for WeatherTool."""
    
    def test_weather_tool_initialization(self, weather_tool):
        """Test weather tool initializes correctly."""
        assert weather_tool.name == "get_weather"
        assert "weather" in weather_tool.description.lower()
    
    def test_execute_with_location(self, weather_tool, sample_weather_response):
        """Test weather retrieval with specific location."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = sample_weather_response
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = weather_tool.execute(location="New York")
            
            assert result["success"] is True
            assert "temperature" in result
            assert "weather" in result
            assert result["location"] == "New York"
    
    def test_execute_without_location(self, weather_tool, sample_weather_response):
        """Test weather retrieval using current GPS location."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = sample_weather_response
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = weather_tool.execute()
            
            assert result["success"] is True
            assert "temperature" in result
    
    def test_execute_api_failure(self, weather_tool):
        """Test weather tool handles API failures gracefully."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            result = weather_tool.execute(location="Invalid")
            
            assert result["success"] is False
            assert "error" in result
    
    def test_validate_inputs(self, weather_tool):
        """Test input validation."""
        assert weather_tool.validate_inputs() is True
        assert weather_tool.validate_inputs(location="New York") is True


class TestUberTool:
    """Test cases for UberTool."""
    
    def test_uber_tool_initialization(self, uber_tool):
        """Test Uber tool initializes correctly."""
        assert uber_tool.name == "book_uber_ride"
        assert "uber" in uber_tool.description.lower()
    
    def test_execute_with_destination(self, uber_tool):
        """Test Uber link generation with destination."""
        result = uber_tool.execute(destination="Times Square, NY")
        
        assert result["success"] is True
        assert "deep_link" in result
        assert "destination" in result
        assert result["destination"] == "Times Square, NY"
        assert "uber" in result["deep_link"].lower()
    
    def test_execute_with_pickup_and_destination(self, uber_tool):
        """Test Uber link generation with both pickup and destination."""
        result = uber_tool.execute(
            pickup="Central Park, NY",
            destination="Times Square, NY"
        )
        
        assert result["success"] is True
        assert "pickup_location" in result
        assert result["pickup_location"] == "Central Park, NY"
    
    def test_execute_invalid_destination(self, uber_tool, mock_location_service):
        """Test Uber tool with invalid destination."""
        mock_location_service.geocode_address.return_value = None
        
        result = uber_tool.execute(destination="Invalid Location XYZ")
        
        assert result["success"] is False
        assert "error" in result
    
    def test_validate_inputs(self, uber_tool):
        """Test input validation."""
        assert uber_tool.validate_inputs(destination="Times Square") is True
        assert uber_tool.validate_inputs(destination="") is False
        assert uber_tool.validate_inputs() is False


class TestZomatoTool:
    """Test cases for ZomatoTool."""
    
    def test_zomato_tool_initialization(self, zomato_tool):
        """Test Zomato tool initializes correctly."""
        assert zomato_tool.name == "search_restaurants"
        assert "restaurant" in zomato_tool.description.lower()
    
    def test_execute_with_query(self, zomato_tool, sample_restaurants):
        """Test restaurant search with query."""
        # Zomato tool will use mock data if API key not configured
        result = zomato_tool.execute(query="Italian")
        
        assert result["success"] is True
        assert "restaurants" in result
        assert len(result["restaurants"]) > 0
        assert result["query"] == "Italian"
    
    def test_execute_with_location(self, zomato_tool):
        """Test restaurant search with specific location."""
        result = zomato_tool.execute(
            query="Chinese",
            location="Brooklyn, NY"
        )
        
        assert result["success"] is True
        assert "restaurants" in result
    
    def test_execute_with_limit(self, zomato_tool):
        """Test restaurant search with result limit."""
        result = zomato_tool.execute(query="Mexican", limit=2)
        
        assert result["success"] is True
        assert len(result["restaurants"]) <= 2
    
    def test_mock_results_generation(self, zomato_tool):
        """Test mock results generation for common cuisines."""
        cuisines = ["Italian", "Chinese", "Mexican"]
        
        for cuisine in cuisines:
            result = zomato_tool._get_mock_results(cuisine, "New York", 3)
            
            assert result["success"] is True
            assert len(result["restaurants"]) > 0
            assert result["query"] == cuisine
    
    def test_validate_inputs(self, zomato_tool):
        """Test input validation."""
        assert zomato_tool.validate_inputs(query="Italian") is True
        assert zomato_tool.validate_inputs(query="") is False
        assert zomato_tool.validate_inputs() is False


class TestToolCallability:
    """Test that tools are callable."""
    
    def test_weather_tool_callable(self, weather_tool, sample_weather_response):
        """Test weather tool can be called directly."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = sample_weather_response
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = weather_tool(location="New York")
            
            assert isinstance(result, dict)
            assert "success" in result
    
    def test_uber_tool_callable(self, uber_tool):
        """Test Uber tool can be called directly."""
        result = uber_tool(destination="Times Square")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_zomato_tool_callable(self, zomato_tool):
        """Test Zomato tool can be called directly."""
        result = zomato_tool(query="Italian")
        
        assert isinstance(result, dict)
        assert "success" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
