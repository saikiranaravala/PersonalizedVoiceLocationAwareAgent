"""Weather information tool."""

from typing import Any, Dict

import requests

from tools.base import BaseTool
from utils.config import config
from utils.logger import logger


class WeatherTool(BaseTool):
    """Tool for getting weather information."""

    name = "get_weather"
    description = "Get current weather information for a location. Input should be a location string (city, address) or leave empty to use current GPS location."

    def __init__(self, location_service):
        """Initialize weather tool.
        
        Args:
            location_service: LocationService instance for GPS
        """
        super().__init__()
        self.location_service = location_service

    def execute(self, location: str = None, **kwargs) -> Dict[str, Any]:
        """Get weather information.

        Args:
            location: Location string or None for current location
            **kwargs: Additional arguments

        Returns:
            Weather information dictionary
        """
        # Get coordinates
        if location:
            coords = self.location_service.geocode_address(location)
            if not coords:
                return {
                    "success": False,
                    "error": f"Could not find location: {location}"
                }
            lat, lon = coords
            location_name = location
        else:
            # Use current GPS location
            current_loc = self.location_service.get_current_location()
            lat = current_loc["latitude"]
            lon = current_loc["longitude"]
            location_name = current_loc.get("city", "your location")

        try:
            # Using open-meteo.com (free, no API key required)
            url = f"https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "temperature_unit": "fahrenheit",
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data.get("current_weather", {})
            
            # Map weather codes to descriptions
            weather_codes = {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Foggy",
                48: "Depositing rime fog",
                51: "Light drizzle",
                53: "Moderate drizzle",
                55: "Dense drizzle",
                61: "Slight rain",
                63: "Moderate rain",
                65: "Heavy rain",
                71: "Slight snow",
                73: "Moderate snow",
                75: "Heavy snow",
                77: "Snow grains",
                80: "Slight rain showers",
                81: "Moderate rain showers",
                82: "Violent rain showers",
                85: "Slight snow showers",
                86: "Heavy snow showers",
                95: "Thunderstorm",
                96: "Thunderstorm with slight hail",
                99: "Thunderstorm with heavy hail",
            }
            
            weather_code = current.get("weathercode", 0)
            weather_desc = weather_codes.get(weather_code, "Unknown")
            
            result = {
                "success": True,
                "location": location_name,
                "latitude": lat,
                "longitude": lon,
                "temperature": current.get("temperature"),
                "temperature_unit": "°F",
                "weather": weather_desc,
                "wind_speed": current.get("windspeed"),
                "wind_speed_unit": "mph",
                "time": current.get("time"),
                "summary": f"Current weather in {location_name}: {weather_desc}, {current.get('temperature')}°F"
            }
            
            logger.info(f"Weather retrieved for {location_name}: {weather_desc}, {current.get('temperature')}°F")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Weather API request failed: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch weather data: {str(e)}"
            }
        except Exception as e:
            return self.handle_error(e)

    def validate_inputs(self, location: str = None, **kwargs) -> bool:
        """Validate weather tool inputs.

        Args:
            location: Location string (optional)
            **kwargs: Additional arguments

        Returns:
            True if valid
        """
        # Location is optional, so always valid
        return True
