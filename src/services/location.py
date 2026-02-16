"""Location services for GPS and geocoding."""

from typing import Dict, Optional, Tuple

import geocoder
from geopy.geocoders import Nominatim

from utils.config import config
from utils.logger import logger


class LocationService:
    """Service for handling location-related operations."""

    def __init__(self):
        """Initialize location service."""
        self.geolocator = Nominatim(user_agent="personalized_agentic_assistant")
        self.use_gps = config.get("location.use_gps", True)
        self.fallback_location = config.get("location.fallback_location", "New York, NY")
        self._current_location = None

    def get_current_location(self) -> Dict[str, any]:
        """Get current GPS location.

        Returns:
            Dictionary with latitude, longitude, and address
        """
        if not self.use_gps:
            logger.info("GPS disabled, using fallback location")
            return self._get_fallback_location()

        try:
            # Try to get GPS location
            g = geocoder.ip('me')
            
            if g.ok and g.latlng:
                lat, lng = g.latlng
                address = g.address or "Unknown"
                
                self._current_location = {
                    "latitude": lat,
                    "longitude": lng,
                    "address": address,
                    "city": g.city,
                    "country": g.country,
                }
                
                logger.info(f"GPS location acquired: {address}")
                return self._current_location
            else:
                logger.warning("Could not determine GPS location, using fallback")
                return self._get_fallback_location()
                
        except Exception as e:
            logger.error(f"Error getting GPS location: {e}")
            return self._get_fallback_location()

    def _get_fallback_location(self) -> Dict[str, any]:
        """Get fallback location from configuration.

        Returns:
            Dictionary with fallback location details
        """
        try:
            location = self.geolocator.geocode(self.fallback_location)
            
            if location:
                return {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "address": location.address,
                    "city": self.fallback_location,
                    "country": "USA",
                }
        except Exception as e:
            logger.error(f"Error geocoding fallback location: {e}")
        
        # Ultimate fallback - default coordinates
        return {
            "latitude": config.get_env("DEFAULT_LATITUDE", 40.7128),
            "longitude": config.get_env("DEFAULT_LONGITUDE", -74.0060),
            "address": self.fallback_location,
            "city": self.fallback_location,
            "country": "USA",
        }

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Convert address to coordinates.

        Args:
            address: Address string to geocode

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            location = self.geolocator.geocode(address)
            if location:
                logger.info(f"Geocoded address '{address}' to {location.latitude}, {location.longitude}")
                return (location.latitude, location.longitude)
            else:
                logger.warning(f"Could not geocode address: {address}")
                return None
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """Convert coordinates to address.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Address string or None if not found
        """
        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}")
            if location:
                logger.info(f"Reverse geocoded {latitude}, {longitude} to {location.address}")
                return location.address
            else:
                logger.warning(f"Could not reverse geocode coordinates")
                return None
        except Exception as e:
            logger.error(f"Error reverse geocoding: {e}")
            return None

    def get_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers.

        Args:
            lat1: First latitude
            lon1: First longitude
            lat2: Second latitude
            lon2: Second longitude

        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2

        # Haversine formula
        R = 6371  # Earth's radius in kilometers

        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)

        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance
