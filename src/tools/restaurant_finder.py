import urllib.request
import urllib.parse
import json
import math
import sys
from typing import Union
from tools import BaseTool


class RestaurantFinder(BaseTool):
    """
    🍽️  Local Restaurant Finder — 100% Free, No API Key Required
    Uses:
    - ipinfo.io        → detect your location from IP (free)
    - Nominatim (OSM)  → reverse geocode city name to lat/lon (free)
    - Overpass API     → query real OpenStreetMap restaurant data (free)
    """

    name = "search_restaurants"
    description = (
        "Search for restaurants near a location. "
        "Requires 'query' (cuisine type or restaurant name). "
        "Optionally accepts 'location' (string city name OR dict with lat/lon, "
        "defaults to current GPS location) and 'limit' (default 5)."
    )

    def __init__(self, location_service=None):
        """Initialize RestaurantFinder with optional location service."""
        super().__init__()
        self.location_service = location_service

    # ──────────────────────────────────────────────
    # PUBLIC ENTRY POINT
    # ──────────────────────────────────────────────

    def execute(
        self,
        query: str,
        location: Union[str, dict, None] = None,  # FIX 1: accept str OR dict
        limit: int = 5,
        radius_meters: int = 3000,
        **kwargs,
    ) -> dict:
        """Execute a restaurant search and return structured results.

        Args:
            query: Cuisine or restaurant name to search for.
            location: Optional city name string (e.g. "New York City") OR
                      dict with `lat` and `lon` keys, OR None to use
                      location_service / IP-based detection.
            limit: Maximum number of results to return.
            radius_meters: Search radius in meters.

        Returns:
            Dict containing `success`, `count`, and `restaurants` list,
            or an error payload.
        """
        try:
            lat, lon = self._resolve_location(location)
            elements = self._search_restaurants(lat, lon, query, radius_meters=radius_meters)
            restaurants = self._parse_results(elements, lat, lon)
            restaurants = restaurants[: max(0, int(limit))]

            return {
                "success": True,
                "count": len(restaurants),
                "restaurants": restaurants,
            }
        except Exception as e:
            return self.handle_error(e)

    # ──────────────────────────────────────────────
    # FIX 1 + FIX 3: location resolver
    # Handles str, dict, location_service, and IP fallback
    # ──────────────────────────────────────────────

    def _resolve_location(self, location: Union[str, dict, None]) -> tuple:
        """Return (lat, lon) from whatever location input is provided.

        Resolution order:
          1. Explicit dict  {"lat": .., "lon": ..}  or  {"latitude": .., "longitude": ..}
          2. Explicit string city name  "New York City"
          3. ContextManager  → get_location() → {"latitude", "longitude", ...}
          4. LocationService → get_current_location() → {"latitude", "longitude", ...}
          5. IP-based fallback
        """

        # Case 1: explicit dict — support both key conventions
        if isinstance(location, dict):
            # Support both {"lat","lon"} and {"latitude","longitude"}
            lat = location.get("lat") or location.get("latitude")
            lon = location.get("lon") or location.get("longitude")
            if lat is None or lon is None:
                raise ValueError(
                    "location dict must contain 'lat'/'lon' or 'latitude'/'longitude' keys."
                )
            return float(lat), float(lon)

        # Case 2: string city name  "New York City"
        if isinstance(location, str) and location.strip():
            return self._geocode_city(location.strip())

        # Case 3 & 4: use injected service (ContextManager or LocationService)
        if self.location_service is not None:
            coords = self._coords_from_service(self.location_service)
            if coords is not None:
                return coords

        # Case 5: final fallback — IP-based detection
        lat, lon, _ = self._get_location_from_ip()
        return lat, lon

    @staticmethod
    def _coords_from_service(svc) -> tuple | None:
        """
        Extract (lat, lon) from either of the two real service types:

        ContextManager  (services/context.py)
            svc.get_location()
            → {"latitude": float, "longitude": float, "address": str, ...}
            → or None if location was never set

        LocationService  (services/location.py)
            svc.get_current_location()
            → {"latitude": float, "longitude": float, "address": str, ...}
            → always returns a dict (falls back to config default)
        """

        def _extract(d: dict) -> tuple | None:
            """Pull (lat, lon) from a location dict using either key convention."""
            if not isinstance(d, dict):
                return None
            lat = d.get("latitude") or d.get("lat")
            lon = d.get("longitude") or d.get("lon")
            if lat is not None and lon is not None:
                return float(lat), float(lon)
            return None

        # ── ContextManager: get_location() ──────────────────────
        # Returns current_location dict, or None if never set via set_location()
        if callable(getattr(svc, "get_location", None)):
            try:
                result = svc.get_location()
                if result is not None:
                    coords = _extract(result)
                    if coords:
                        return coords
                    # get_location() returned something but coords missing — log it
                    from utils.logger import logger
                    logger.warning(
                        f"ContextManager.get_location() returned unexpected shape: {result}. "
                        f"Expected keys: 'latitude' and 'longitude'."
                    )
                else:
                    # None means set_location() was never called — fall through to LocationService
                    from utils.logger import logger
                    logger.debug("ContextManager.get_location() returned None — location not yet set.")
            except Exception as e:
                from utils.logger import logger
                logger.error(f"Error calling get_location() on context manager: {e}")

        # ── LocationService: get_current_location() ─────────────
        # Always returns a dict; uses GPS → IP → config fallback internally
        if callable(getattr(svc, "get_current_location", None)):
            try:
                result = svc.get_current_location()
                if result is not None:
                    coords = _extract(result)
                    if coords:
                        return coords
                    from utils.logger import logger
                    logger.warning(
                        f"LocationService.get_current_location() returned unexpected shape: {result}. "
                        f"Expected keys: 'latitude' and 'longitude'."
                    )
            except Exception as e:
                from utils.logger import logger
                logger.error(f"Error calling get_current_location() on location service: {e}")

        return None  # Both services failed — caller will fall back to IP

    # ──────────────────────────────────────────────
    # 1. DETECT LOCATION FROM IP
    # ──────────────────────────────────────────────

    @staticmethod  # FIX 2: all helpers are @staticmethod (no implicit self)
    def _get_location_from_ip():
        """Uses ipinfo.io to get approximate lat/lon from your IP."""
        url = "https://ipinfo.io/json"
        req = urllib.request.Request(url, headers={"User-Agent": "RestaurantFinder/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        loc = data.get("loc", "")
        if not loc:
            raise ValueError("Could not determine location from IP.")
        lat, lon = map(float, loc.split(","))
        city = data.get("city", "Unknown City")
        region = data.get("region", "")
        print(f"📍 Detected location: {city}, {region} ({lat:.4f}, {lon:.4f})")
        return lat, lon, city

    @staticmethod
    def _geocode_city(city_name: str) -> tuple:
        """Convert a city name string → (lat, lon) using free Nominatim API."""
        params = urllib.parse.urlencode({"q": city_name, "format": "json", "limit": 1})
        url = f"https://nominatim.openstreetmap.org/search?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "RestaurantFinder/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            results = json.loads(resp.read().decode())
        if not results:
            raise ValueError(f"Could not geocode city: '{city_name}'")
        return float(results[0]["lat"]), float(results[0]["lon"])

    # ──────────────────────────────────────────────
    # 2. SEARCH RESTAURANTS VIA OVERPASS API
    # ──────────────────────────────────────────────

    CUISINE_MAP = {
        "indian":        ["indian"],
        "biryani":       ["indian"],          # common LLM query
        "chinese":       ["chinese"],
        "italian":       ["italian", "pizza"],
        "mexican":       ["mexican"],
        "japanese":      ["japanese", "sushi", "ramen"],
        "thai":          ["thai"],
        "american":      ["american", "burger", "fast_food"],
        "pizza":         ["pizza", "italian"],
        "sushi":         ["sushi", "japanese"],
        "burger":        ["burger", "american"],
        "vegan":         ["vegan", "vegetarian"],
        "vegetarian":    ["vegetarian", "vegan"],
        "mediterranean": ["mediterranean", "greek", "lebanese"],
        "french":        ["french"],
        "korean":        ["korean"],
        "vietnamese":    ["vietnamese"],
        "seafood":       ["seafood", "fish_and_chips"],
        "bbq":           ["bbq", "american"],
        "cafe":          ["coffee_shop", "cafe"],
        "breakfast":     ["breakfast", "american"],
    }

    @staticmethod
    def _build_overpass_query(lat, lon, cuisine_tags, radius_meters=3000):
        """Build an Overpass QL query for restaurants with given cuisine tags."""
        tag_filters = ""
        for tag in cuisine_tags:
            tag_filters += (
                f'  node(around:{radius_meters},{lat},{lon})[amenity=restaurant][cuisine~"{tag}",i];\n'
                f'  way(around:{radius_meters},{lat},{lon})[amenity=restaurant][cuisine~"{tag}",i];\n'
            )
        # Fallback: any nearby restaurant regardless of cuisine tag
        tag_filters += (
            f'  node(around:{radius_meters},{lat},{lon})[amenity=restaurant];\n'
            f'  way(around:{radius_meters},{lat},{lon})[amenity=restaurant];\n'
        )
        return f"[out:json][timeout:25];\n(\n{tag_filters});\nout body center 30;"

    def _search_restaurants(self, lat, lon, cuisine_input, radius_meters=3000):
        """Query Overpass API for nearby restaurants matching the cuisine."""
        cuisine_key = cuisine_input.lower().strip()
        cuisine_tags = self.CUISINE_MAP.get(cuisine_key, [cuisine_key])

        print(f"\n🔍 Searching for '{cuisine_input}' restaurants within {radius_meters / 1000:.1f} km...")

        query = self._build_overpass_query(lat, lon, cuisine_tags, radius_meters)
        encoded = urllib.parse.urlencode({"data": query}).encode()
        url = "https://overpass-api.de/api/interpreter"

        req = urllib.request.Request(url, data=encoded, headers={"User-Agent": "RestaurantFinder/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        return data.get("elements", [])

    # ──────────────────────────────────────────────
    # 3. PARSE & FORMAT RESULTS
    # ──────────────────────────────────────────────

    @staticmethod
    def _haversine_km(lat1, lon1, lat2, lon2):
        """Calculate distance in km between two lat/lon points."""
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return R * 2 * math.asin(math.sqrt(a))

    @staticmethod
    def _parse_results(elements, user_lat, user_lon):
        """Extract and deduplicate restaurant info from OSM elements."""
        seen = set()
        restaurants = []

        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name")
            if not name or name in seen:
                continue
            seen.add(name)

            if el["type"] == "node":
                lat, lon = el.get("lat"), el.get("lon")
            else:
                center = el.get("center", {})
                lat, lon = center.get("lat"), center.get("lon")

            if lat is None or lon is None:
                continue

            dist = RestaurantFinder._haversine_km(user_lat, user_lon, lat, lon)

            restaurants.append({
                "name":          name,
                "cuisine":       tags.get("cuisine", "N/A").replace(";", ", "),
                "address":       ", ".join(
                    filter(None, [
                        tags.get("addr:housenumber", ""),
                        tags.get("addr:street", ""),
                        tags.get("addr:city", ""),
                    ])
                ) or "Address not listed",
                "phone":         tags.get("phone") or tags.get("contact:phone", "N/A"),
                "website":       tags.get("website") or tags.get("contact:website", "N/A"),
                "opening_hours": tags.get("opening_hours", "N/A"),
                "distance_km":   round(dist, 2),
                "lat":           lat,
                "lon":           lon,
            })

        restaurants.sort(key=lambda r: r["distance_km"])
        return restaurants

    # ──────────────────────────────────────────────
    # 4. DISPLAY RESULTS
    # ──────────────────────────────────────────────

    @staticmethod
    def print_restaurants(restaurants, cuisine):
        if not restaurants:
            print(f"\n😕 No '{cuisine}' restaurants found nearby in OpenStreetMap data.")
            print("   Try a broader cuisine (e.g. 'indian', 'chinese') or increase the search radius.")
            return

        print(f"\n{'═' * 55}")
        print(f"  🍽️  Found {len(restaurants)} '{cuisine}' restaurant(s) near you")
        print(f"{'═' * 55}")

        for i, r in enumerate(restaurants[:15], 1):
            print(f"\n  #{i}  {r['name']}")
            print(f"       📏 {r['distance_km']} km away")
            print(f"       🍴 Cuisine : {r['cuisine']}")
            print(f"       📍 Address : {r['address']}")
            print(f"       📞 Phone   : {r['phone']}")
            print(f"       🌐 Website : {r['website']}")
            print(f"       🕐 Hours   : {r['opening_hours']}")

        print(f"\n{'═' * 55}\n")

    # ──────────────────────────────────────────────
    # 5. MAIN (standalone / CLI use)
    # ──────────────────────────────────────────────

    @staticmethod
    def main():
        print("=" * 55)
        print("   🍽️  Local Restaurant Finder (Free / No API Key)")
        print("=" * 55)

        if len(sys.argv) > 1:
            cuisine = " ".join(sys.argv[1:])
        else:
            print("\nAvailable cuisines: indian, chinese, italian, mexican,")
            print("  japanese, thai, american, pizza, sushi, burger,")
            print("  vegan, vegetarian, mediterranean, french, korean,")
            print("  vietnamese, seafood, bbq, cafe, breakfast, or any custom tag\n")
            cuisine = input("Enter cuisine type: ").strip()

        if not cuisine:
            print("No cuisine entered. Exiting.")
            sys.exit(1)

        finder = RestaurantFinder()

        try:
            lat, lon, city = RestaurantFinder._get_location_from_ip()
        except Exception as e:
            print(f"❌ Location detection failed: {e}")
            lat = float(input("Enter latitude (e.g. 42.12): "))
            lon = float(input("Enter longitude (e.g. -80.08): "))

        try:
            elements = finder._search_restaurants(lat, lon, cuisine, radius_meters=5000)
        except Exception as e:
            print(f"❌ Overpass API error: {e}")
            sys.exit(1)

        restaurants = RestaurantFinder._parse_results(elements, lat, lon)
        RestaurantFinder.print_restaurants(restaurants, cuisine)

        if restaurants:
            out_file = f"{cuisine.replace(' ', '_')}_restaurants.json"
            with open(out_file, "w") as f:
                json.dump(restaurants, f, indent=2)
            print(f"💾 Results saved to: {out_file}")


if __name__ == "__main__":
    RestaurantFinder.main()
