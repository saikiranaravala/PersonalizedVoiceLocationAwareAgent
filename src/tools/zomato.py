"""Zomato restaurant search tool."""

from typing import Any, Dict, List

import requests

from tools.base import BaseTool
from utils.config import config
from utils.logger import logger


class ZomatoTool(BaseTool):
    """Tool for searching restaurants using Zomato API."""

    name = "search_restaurants"
    description = (
        "Search for restaurants near a location. "
        "Requires 'query' (cuisine type or restaurant name). "
        "Optionally accepts 'location' (defaults to current GPS location) and 'limit' (default 5)."
    )

    def __init__(self, location_service):
        """Initialize Zomato tool.
        
        Args:
            location_service: LocationService instance for GPS
        """
        super().__init__()
        self.location_service = location_service
        self.api_key = config.zomato_api_key
        self.base_url = config.get("tools.zomato.base_url", "https://developers.zomato.com/api/v2.1")

    def execute(self, query: str, location: str = None, limit: int = 5, **kwargs) -> Dict[str, Any]:
        """Search for restaurants.

        Args:
            query: Search query (cuisine, restaurant name, etc.)
            location: Location string or None for current location
            limit: Maximum number of results (default 5)
            **kwargs: Additional arguments

        Returns:
            Dictionary with restaurant results
        """
        # Check if API key is available
        if not self.api_key:
            logger.warning("Zomato API key not configured, using mock data")
            return self._get_mock_results(query, location, limit)

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
            # Search restaurants using coordinates
            headers = {
                "user-key": self.api_key,
                "Accept": "application/json"
            }
            
            params = {
                "q": query,
                "lat": lat,
                "lon": lon,
                "count": min(limit, 20),  # Zomato max is 20
                "sort": "rating",
                "order": "desc"
            }
            
            response = requests.get(
                f"{self.base_url}/search",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 403:
                logger.warning("Zomato API access forbidden, using mock data")
                return self._get_mock_results(query, location_name, limit)
            
            response.raise_for_status()
            data = response.json()
            
            restaurants = []
            for item in data.get("restaurants", [])[:limit]:
                rest = item.get("restaurant", {})
                restaurants.append({
                    "name": rest.get("name"),
                    "cuisine": rest.get("cuisines"),
                    "rating": rest.get("user_rating", {}).get("aggregate_rating"),
                    "address": rest.get("location", {}).get("address"),
                    "price_range": rest.get("price_range"),
                    "url": rest.get("url"),
                })
            
            result = {
                "success": True,
                "query": query,
                "location": location_name,
                "count": len(restaurants),
                "restaurants": restaurants,
                "message": f"Found {len(restaurants)} restaurants matching '{query}' near {location_name}"
            }
            
            logger.info(f"Found {len(restaurants)} restaurants for query: {query}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Zomato API request failed: {e}")
            logger.info("Falling back to mock data")
            return self._get_mock_results(query, location_name, limit)
        except Exception as e:
            return self.handle_error(e)

    def _get_mock_results(self, query: str, location: str, limit: int) -> Dict[str, Any]:
        """Generate mock restaurant results for demonstration.

        Args:
            query: Search query
            location: Location name
            limit: Number of results

        Returns:
            Mock results dictionary
        """
        # Sample mock data for common cuisines
        mock_restaurants = {
            "italian": [
                {"name": "Falcone's Kitchen", "cuisine": "Italian", "rating": 4.5, "address": "2901 Copperleaf Dr, Erie, PA 16506", "price_range": 3},
                {"name": "Olive Garden Italian Restaurant", "cuisine": "Italian", "rating": 4.3, "address": "5945 Peach St, Erie, PA 16509", "price_range": 2},
                {"name": "The Cork 1794", "cuisine": "Italian", "rating": 4.7, "address": "900 W Erie Plaza Dr, Erie, PA 16505", "price_range": 4},
            ],
            "chinese": [
                {"name": "Kirin Court", "cuisine": "Chinese", "rating": 4.7, "address": "5624 Peach St, Erie, PA 16509", "price_range": 10-20},
                {"name": "Yummy Bowl", "cuisine": "Chinese", "rating": 4.6, "address": "2421 Asbury Rd, Erie, PA 16506", "price_range": 10-15},
                {"name": "Imperial Buffet", "cuisine": "Chinese", "rating": 4.3, "address": "7200 Peach St Suite 14, Erie, PA 16509", "price_range": 15-18},
            ],
            "mexican": [
                {"name": "Chipotle Mexican Grill", "cuisine": "Mexican", "rating": 4.3, "address": "6611 Peach St, Erie, PA 16509", "price_range": 10-20},
                {"name": "El Amigo Mexican Grill", "cuisine": "Mexican", "rating": 4.4, "address": "333 State St, Erie, PA 16507", "price_range": 20-30},
                {"name": "El Canelo Mexican Restaurant", "cuisine": "Mexican", "rating": 4.5, "address": "2709 W 12th St, Erie, PA 16505", "price_range": 10-20},
            ],
            "indian": [
                {"name": "Kadhai Kitchen", "cuisine": "Indian", "rating": 4.8, "address": "5901 W Ridge Rd, Erie, PA 16506", "price_range": 20-30},
                {"name": "Biryani Bowl", "cuisine": "Indian", "rating": 4.5, "address": "1707 State St, Erie, PA 16501", "price_range": 10-20},
                {"name": "Tandoori Hut Indian Cuisine", "cuisine": "Indian", "rating": 4.3, "address": "2605 Washington Ave, Erie, PA 16508", "price_range": 10-20},
            ],
            "thai": [
                {"name": "Thai Eatery", "cuisine": "Thai", "rating": 4.6, "address": "5641 Peach St, Erie, PA 16509", "price_range": 10-20},
                {"name": "Thai Taste Cuisine", "cuisine": "Thai", "rating": 4.7, "address": "35 Peninsula Dr, Erie, PA 16505", "price_range": 10},
                {"name": "Chopstix Express", "cuisine": "Thai", "rating": 4.2, "address": "3842 Liberty St, Erie, PA 16509", "price_range": 10-20},
            ],
        }
        
        # Find matching cuisine or use default
        query_lower = query.lower()
        restaurants = []
        
        for cuisine_type, resto_list in mock_restaurants.items():
            if cuisine_type in query_lower:
                restaurants = resto_list[:limit]
                break
        
        # Default generic restaurants if no match
        if not restaurants:
            restaurants =[
                {"name": "Kadhai Kitchen", "cuisine": "Indian", "rating": 4.8, "address": "5901 W Ridge Rd, Erie, PA 16506", "price_range": 20-30},
                {"name": "Chipotle Mexican Grill", "cuisine": "Mexican", "rating": 4.3, "address": "6611 Peach St, Erie, PA 16509", "price_range": 10-20},
                {"name": "Olive Garden Italian Restaurant", "cuisine": "Italian", "rating": 4.3, "address": "5945 Peach St, Erie, PA 16509", "price_range": 20-25}            
            ]
        
        return {
            "success": True,
            "query": query,
            "location": location or "your location",
            "count": len(restaurants),
            "restaurants": restaurants,
            "message": f"Found {len(restaurants)} restaurants (mock data) matching '{query}'",
            "note": "Using mock data - Configure ZOMATO_API_KEY for real results"
        }

    def validate_inputs(self, query: str = None, **kwargs) -> bool:
        """Validate Zomato tool inputs.

        Args:
            query: Search query (required)
            **kwargs: Additional arguments

        Returns:
            True if valid, False otherwise
        """
        if not query or not isinstance(query, str) or not query.strip():
            logger.warning("Invalid query provided to Zomato tool")
            return False
        return True
