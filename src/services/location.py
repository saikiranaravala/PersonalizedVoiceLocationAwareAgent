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
        # Initialize with a proper user agent and timeout
        self.geolocator = Nominatim(
            user_agent="personalized_agentic_assistant/1.0",
            timeout=10
        )
        self.use_gps = config.get("location.use_gps", True)
        self.fallback_location = config.get("location.fallback_location", "New York, NY")
        self._current_location = None
        
        # Cache for geocoded addresses to avoid repeated API calls
        self._geocode_cache = {}

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
        """Convert address to coordinates with multiple attempts.

        Args:
            address: Address string to geocode

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        # Check cache first
        if address in self._geocode_cache:
            logger.debug(f"Using cached coordinates for: {address}")
            return self._geocode_cache[address]
        
        # Try different address formats for better success rate
        address_variants = [
            address,  # Full address as provided
            # Extract just street address and city if full format
            self._simplify_address(address),
        ]
        
        for variant in address_variants:
            if not variant:
                continue
                
            try:
                # Attempt geocoding with timeout
                location = self.geolocator.geocode(variant, timeout=10)
                
                if location:
                    coords = (location.latitude, location.longitude)
                    logger.info(f"Geocoded address '{variant}' to {coords[0]}, {coords[1]}")
                    
                    # Cache the result
                    self._geocode_cache[address] = coords
                    return coords
                else:
                    logger.debug(f"No results for address variant: {variant}")
                    
            except Exception as e:
                logger.debug(f"Error geocoding variant '{variant}': {e}")
                continue
        
        # If all attempts failed
        logger.warning(f"Could not geocode address after trying multiple formats: {address}")
        
        # Try one more time with just the ZIP code or city
        zip_match = self._extract_zip_or_city(address)
        if zip_match:
            try:
                location = self.geolocator.geocode(zip_match, timeout=10)
                if location:
                    coords = (location.latitude, location.longitude)
                    logger.info(f"Geocoded using ZIP/city '{zip_match}' to {coords[0]}, {coords[1]}")
                    
                    # Cache the result
                    self._geocode_cache[address] = coords
                    return coords
            except Exception as e:
                logger.debug(f"Final geocoding attempt failed: {e}")
        
        # Cache negative result to avoid repeated failures
        self._geocode_cache[address] = None
        return None

    def _simplify_address(self, address: str) -> Optional[str]:
        """Simplify address by removing business names and keeping core address.
        
        Args:
            address: Full address string
            
        Returns:
            Simplified address or None
        """
        # If address contains comma, try taking parts after first comma
        # "Olive Garden, 5945 Peach St, Erie, PA" -> "5945 Peach St, Erie, PA"
        if ',' in address:
            parts = address.split(',')
            if len(parts) > 1:
                # Skip first part (likely business name) if it doesn't start with a number
                if not parts[0].strip()[0].isdigit():
                    return ','.join(parts[1:]).strip()
        
        return None

    def _extract_zip_or_city(self, address: str) -> Optional[str]:
        """Extract ZIP code or city from address for fallback geocoding.
        
        Args:
            address: Full address string
            
        Returns:
            ZIP code or city name
        """
        import re
        
        # Try to find ZIP code (US format: 5 digits or 5+4)
        zip_match = re.search(r'\b\d{5}(?:-\d{4})?\b', address)
        if zip_match:
            return zip_match.group(0)
        
        # Try to extract city and state (e.g., "Erie, PA")
        # Look for pattern: Word, STATE_CODE
        city_state = re.search(r',\s*([A-Za-z\s]+),\s*([A-Z]{2})', address)
        if city_state:
            return f"{city_state.group(1)}, {city_state.group(2)}"
        
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
