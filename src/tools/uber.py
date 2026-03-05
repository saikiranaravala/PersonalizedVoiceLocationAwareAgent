"""Uber ride booking tool with deep linking."""

from typing import Any, Dict
from urllib.parse import quote

from tools.base import BaseTool
from utils.logger import logger


class UberTool(BaseTool):
    """Tool for generating Uber deep links to book rides."""

    name = "book_uber_ride"
    description = (
        "Generate a link to book an Uber ride. "
        "Requires 'destination' (address or place name). "
        "Optionally accepts 'pickup' location (defaults to current GPS location)."
    )

    def __init__(self, location_service):
        """Initialize Uber tool.
        
        Args:
            location_service: LocationService instance for GPS
        """
        super().__init__()
        self.location_service = location_service

    def execute(self, destination: str, pickup: str = None, **kwargs) -> Dict[str, Any]:
        """Generate Uber deep link.

        Args:
            destination: Destination address or place name
            pickup: Optional pickup address (uses current location if not provided)
            **kwargs: Additional arguments

        Returns:
            Dictionary with Uber deep link and details
        """
        # Get destination coordinates
        dest_coords = self.location_service.geocode_address(destination)
        if not dest_coords:
            return {
                "success": False,
                "error": f"Could not find destination: {destination}"
            }
        
        dest_lat, dest_lon = dest_coords

        # Get pickup coordinates
        if pickup:
            pickup_coords = self.location_service.geocode_address(pickup)
            if not pickup_coords:
                return {
                    "success": False,
                    "error": f"Could not find pickup location: {pickup}"
                }
            pickup_lat, pickup_lon = pickup_coords
            pickup_name = pickup
        else:
            # Use current GPS location
            current_loc = self.location_service.get_current_location()
            pickup_lat = current_loc["latitude"]
            pickup_lon = current_loc["longitude"]
            pickup_name = current_loc.get("address", "Current Location")

        # Generate Uber deep link (Universal Link format)
        # Modern Uber web app format - uses client_id for better compatibility
        
        # URL-encode the addresses properly
        pickup_encoded = quote(pickup_name, safe='')
        dest_encoded = quote(destination, safe='')
        
        # Uber web deep link - optimized format for web browser
        deep_link = (
            f"https://m.uber.com/looking"
            f"?pickup-latitude={pickup_lat}"
            f"&pickup-longitude={pickup_lon}"
            f"&pickup-nickname={pickup_encoded}"
            f"&dropoff-latitude={dest_lat}"
            f"&dropoff-longitude={dest_lon}"
            f"&dropoff-nickname={dest_encoded}"
        )
        
        # Alternative: Universal Link format (for mobile app)
        universal_link = (
            f"https://m.uber.com/ul/?action=setPickup"
            f"&pickup[latitude]={pickup_lat}"
            f"&pickup[longitude]={pickup_lon}"
            f"&pickup[nickname]={pickup_encoded}"
            f"&dropoff[latitude]={dest_lat}"
            f"&dropoff[longitude]={dest_lon}"
            f"&dropoff[nickname]={dest_encoded}"
        )
        
        # App-based deep link (opens Uber app if installed)
        app_link = (
            f"uber://?action=setPickup"
            f"&pickup[latitude]={pickup_lat}"
            f"&pickup[longitude]={pickup_lon}"
            f"&pickup[nickname]={pickup_encoded}"
            f"&dropoff[latitude]={dest_lat}"
            f"&dropoff[longitude]={dest_lon}"
            f"&dropoff[nickname]={dest_encoded}"
        )

        result = {
            "success": True,
            "service": "uber",
            "pickup_location": pickup_name,
            "pickup_coordinates": {"latitude": pickup_lat, "longitude": pickup_lon},
            "destination": destination,
            "destination_coordinates": {"latitude": dest_lat, "longitude": dest_lon},
            "deep_link": deep_link,  # Primary web link
            "universal_link": universal_link,  # Universal link format
            "app_link": app_link,  # App-specific link
            "message": f"Uber ride link generated from {pickup_name} to {destination}",
            "instructions": "Click the link to open Uber and confirm your ride. Pickup and dropoff locations are pre-filled."
        }
        
        logger.info(f"Generated Uber links: {pickup_name} → {destination}")
        logger.info(f"Web link: {deep_link}")
        return result

    def validate_inputs(self, destination: str = None, **kwargs) -> bool:
        """Validate Uber tool inputs.

        Args:
            destination: Destination address (required)
            **kwargs: Additional arguments

        Returns:
            True if valid, False otherwise
        """
        if not destination or not isinstance(destination, str) or not destination.strip():
            logger.warning("Invalid destination provided to Uber tool")
            return False
        return True
