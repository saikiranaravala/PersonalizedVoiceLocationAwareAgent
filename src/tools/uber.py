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

    def execute(self, destination: str, pickup: str = None, user_agent: str = None, 
                user_profile: dict = None, **kwargs) -> Dict[str, Any]:
        """Generate Uber deep link with smart pickup detection.

        Args:
            destination: Destination address or place name
            pickup: Optional explicit pickup address (overrides auto-detection)
            user_agent: HTTP User-Agent header for device detection
            user_profile: User profile data with home address
            **kwargs: Additional arguments

        Returns:
            Dictionary with Uber deep link and details
        """
        from utils.device_detection import should_use_gps
        
        # Get destination coordinates
        dest_coords = self.location_service.geocode_address(destination)
        if not dest_coords:
            return {
                "success": False,
                "error": f"Could not find destination: {destination}"
            }
        
        dest_lat, dest_lon = dest_coords

        # Smart pickup location detection
        if pickup:
            # Explicit pickup provided - use it
            pickup_coords = self.location_service.geocode_address(pickup)
            if not pickup_coords:
                return {
                    "success": False,
                    "error": f"Could not find pickup location: {pickup}"
                }
            pickup_lat, pickup_lon = pickup_coords
            pickup_name = pickup
            pickup_source = "explicit"
            
        elif should_use_gps(user_agent):
            # Mobile device - ALWAYS use current GPS location
            current_loc = self.location_service.get_current_location()
            pickup_lat = current_loc["latitude"]
            pickup_lon = current_loc["longitude"]
            pickup_name = current_loc.get("address", "Current Location")
            pickup_source = "gps"
            logger.info(f"Mobile device detected - using GPS location: {pickup_name}")
            
        else:
            # Desktop - try user profile first, then system location
            if user_profile and user_profile.get("address"):
                # Use address from user profile
                profile_address = user_profile["address"]
                pickup_coords = self.location_service.geocode_address(profile_address)
                
                if pickup_coords:
                    pickup_lat, pickup_lon = pickup_coords
                    pickup_name = profile_address
                    pickup_source = "profile"
                    logger.info(f"Desktop - using profile address: {pickup_name}")
                else:
                    # Profile address geocoding failed - fall back to system location
                    current_loc = self.location_service.get_current_location()
                    pickup_lat = current_loc["latitude"]
                    pickup_lon = current_loc["longitude"]
                    pickup_name = current_loc.get("address", "Current Location")
                    pickup_source = "system_fallback"
                    logger.warning(f"Profile address geocoding failed - using system location: {pickup_name}")
            else:
                # No profile address - use system location
                current_loc = self.location_service.get_current_location()
                pickup_lat = current_loc["latitude"]
                pickup_lon = current_loc["longitude"]
                pickup_name = current_loc.get("address", "Current Location")
                pickup_source = "system"
                logger.info(f"Desktop - no profile address, using system location: {pickup_name}")

        # Generate Uber deep link using ACTUAL WORKING FORMAT
        # Based on real Uber URLs that successfully pre-fill locations
        # Format discovered from working Uber deep links
        
        import json
        import uuid
        
        # Split destination into address lines
        dest_parts = destination.split(',')
        dest_line1 = dest_parts[0].strip() if len(dest_parts) > 0 else destination
        dest_line2 = ', '.join(dest_parts[1:]).strip() if len(dest_parts) > 1 else ""
        
        # Split pickup into address lines  
        pickup_parts = pickup_name.split(',')
        pickup_line1 = pickup_parts[0].strip() if len(pickup_parts) > 0 else pickup_name
        pickup_line2 = ', '.join(pickup_parts[1:]).strip() if len(pickup_parts) > 1 else ""
        
        # Create pickup JSON object (Uber's actual format)
        pickup_obj = {
            "addressLine1": pickup_line1,
            "addressLine2": pickup_line2,
            "id": str(uuid.uuid4()),
            "source": "SEARCH",
            "latitude": pickup_lat,
            "longitude": pickup_lon,
            "provider": "uber_places"
        }
        
        # Create dropoff JSON object (Uber's actual format)
        dropoff_obj = {
            "addressLine1": dest_line1,
            "addressLine2": dest_line2,
            "id": str(uuid.uuid4()),
            "source": "SEARCH",
            "latitude": dest_lat,
            "longitude": dest_lon,
            "provider": "uber_places"
        }
        
        # URL-encode the JSON objects
        pickup_json = quote(json.dumps(pickup_obj), safe='')
        dropoff_json = quote(json.dumps(dropoff_obj), safe='')
        
        # Generate marketing visitor ID
        visitor_id = str(uuid.uuid4())
        uclick_id = str(uuid.uuid4())
        
        # Uber's ACTUAL working deep link format
        deep_link = (
            f"https://m.uber.com/go/product-selection"
            f"?drop%5B0%5D={dropoff_json}"
            f"&marketing_vistor_id={visitor_id}"
            f"&pickup={pickup_json}"
            f"&uclick_id={uclick_id}"
        )
        
        # Simplified version (without marketing IDs)
        simple_link = (
            f"https://m.uber.com/go/product-selection"
            f"?drop%5B0%5D={dropoff_json}"
            f"&pickup={pickup_json}"
        )
        
        # App protocol link (for mobile with Uber app installed)
        app_link = (
            f"uber://"
            f"?action=setPickup"
            f"&pickup[latitude]={pickup_lat}"
            f"&pickup[longitude]={pickup_lon}"
            f"&pickup[formatted_address]={quote(pickup_name, safe='')}"
            f"&dropoff[latitude]={dest_lat}"
            f"&dropoff[longitude]={dest_lon}"
            f"&dropoff[formatted_address]={quote(destination, safe='')}"
        )

        result = {
            "success": True,
            "service": "uber",
            "pickup_location": pickup_name,
            "pickup_coordinates": {"latitude": pickup_lat, "longitude": pickup_lon},
            "pickup_source": pickup_source,  # NEW: How pickup was determined
            "destination": destination,
            "destination_coordinates": {"latitude": dest_lat, "longitude": dest_lon},
            "deep_link": deep_link,
            "simple_link": simple_link,
            "app_link": app_link,
            "message": self._format_message(pickup_name, destination, pickup_source),
            "instructions": (
                f"Click here to book your Uber: {deep_link}\n\n"
                f"✅ Pickup: {pickup_name} ({self._get_source_label(pickup_source)})\n"
                f"✅ Dropoff: {destination}\n\n"
                f"Both locations are pre-filled. Just verify and confirm!"
            )
        }
        
        logger.info(f"Generated Uber link: {pickup_name} ({pickup_source}) → {destination}")
        logger.info(f"Primary link: {deep_link}")
        logger.info(f"Fallback link: {simple_link}")
        return result
    
    def _format_message(self, pickup: str, destination: str, source: str) -> str:
        """Format user-friendly message based on pickup source."""
        if source == "gps":
            return f"Uber ride from your current location to {destination}"
        elif source == "profile":
            return f"Uber ride from your home ({pickup}) to {destination}"
        elif source == "explicit":
            return f"Uber ride from {pickup} to {destination}"
        else:  # system or system_fallback
            return f"Uber ride from {pickup} to {destination}"
    
    def _get_source_label(self, source: str) -> str:
        """Get user-friendly label for pickup source."""
        labels = {
            "gps": "Current Location",
            "profile": "Your Home",
            "explicit": "Specified",
            "system": "Default Location",
            "system_fallback": "Default Location"
        }
        return labels.get(source, "Location")

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
