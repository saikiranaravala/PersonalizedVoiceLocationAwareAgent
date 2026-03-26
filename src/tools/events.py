"""
Local Public Events Discovery Tool
Uses Ticketmaster Discovery API v2 — requires API key.

Fetches upcoming events for the user's city/state/country over
the next 30 days, sorted by soonest event date, top 10 returned.
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime, timezone, timedelta
from typing import Union

from .base import BaseTool
from utils.logger import logger
from utils.config import config


class EventsTool(BaseTool):
    """
    🎟️  Local Public Events Discovery — Powered by Ticketmaster

    Finds upcoming concerts, sports, theatre, festivals and more
    for the user's city within the next 30 days.
    Returns top 10 events sorted by soonest date, each with a
    direct Ticketmaster link.
    """

    name = "find_local_events"
    description = (
        "Find upcoming local public events (concerts, sports, theatre, festivals, etc.) "
        "near the user's location for the next 30 days. "
        "Accepts optional 'city', 'state_code' (2-letter US state e.g. 'PA'), "
        "'country_code' (default 'US'), and 'keyword' to filter by event type or artist. "
        "Returns top 10 upcoming events with names, dates, venues, and ticket links. "
        "Use when the user asks about events, things to do, concerts, shows, sports, "
        "or entertainment near them."
    )

    # Ticketmaster category IDs for common queries
    SEGMENT_MAP = {
        "music":      "KZFzniwnSyZfZ7v7nJ",
        "concert":    "KZFzniwnSyZfZ7v7nJ",
        "sports":     "KZFzniwnSyZfZ7v7nE",
        "sport":      "KZFzniwnSyZfZ7v7nE",
        "arts":       "KZFzniwnSyZfZ7v7na",
        "theatre":    "KZFzniwnSyZfZ7v7na",
        "theater":    "KZFzniwnSyZfZ7v7na",
        "comedy":     "KZFzniwnSyZfZ7v7na",
        "family":     "KZFzniwnSyZfZ7v7n1",
        "festival":   "KZFzniwnSyZfZ7v7nJ",
        "film":       "KZFzniwnSyZfZ7v7nn",
        "miscellaneous": "KZFzniwnSyZfZ7v7n1",
    }

    def __init__(self, location_service=None):
        super().__init__()
        self.location_service = location_service
        # Load API key from config/.env
        self.api_key = config.get_env("TICKETMASTER_API_KEY", "")
        if not self.api_key:
            logger.warning(
                "TICKETMASTER_API_KEY not set in config/.env — "
                "find_local_events tool will return an error."
            )

    # ─────────────────────────────────────────────────────────
    # PUBLIC ENTRY POINT
    # ─────────────────────────────────────────────────────────

    def execute(
        self,
        city: str = None,
        state_code: str = None,
        country_code: str = "US",
        keyword: str = None,
        limit: int = 10,
        **kwargs,
    ) -> dict:
        """
        Fetch upcoming local events from Ticketmaster.

        Args:
            city:         City name. Falls back to user profile city if omitted.
            state_code:   2-letter state code (e.g. 'PA'). Falls back to profile.
            country_code: ISO 2-letter country code (default 'US').
            keyword:      Optional filter — artist name, event type, or genre.
            limit:        Max events to return (default 10, max 10).

        Returns:
            Dict with 'success', 'count', 'events' list, and 'search_summary'.
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": (
                        "Ticketmaster API key not configured. "
                        "Add TICKETMASTER_API_KEY to config/.env"
                    ),
                    "tool": self.name,
                }

            # Resolve city/state from profile if not explicitly provided
            city, state_code, country_code = self._resolve_location(
                city, state_code, country_code
            )

            # Build date window: now → 30 days
            now = datetime.now(timezone.utc)
            end = now + timedelta(days=30)
            start_dt = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_dt = end.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Map keyword to segment ID if it matches a known category
            segment_id = None
            if keyword:
                segment_id = self.SEGMENT_MAP.get(keyword.lower().strip())

            # Fetch from Ticketmaster
            raw_events = self._fetch_events(
                city=city,
                state_code=state_code,
                country_code=country_code,
                start_dt=start_dt,
                end_dt=end_dt,
                keyword=keyword if not segment_id else None,
                segment_id=segment_id,
                page_size=20,   # fetch 20, return top 10 after sort
            )

            # Parse, sort by date (soonest first), take top N
            events = self._parse_events(raw_events)
            events = events[: max(1, int(limit))]

            location_str = ", ".join(p for p in [city, state_code, country_code] if p)
            search_summary = (
                f"Upcoming events in {location_str}"
                + (f" matching '{keyword}'" if keyword else "")
                + f" — next 30 days"
            )

            logger.info(
                f"[EventsTool] Found {len(events)} events in {location_str}"
                + (f" for '{keyword}'" if keyword else "")
            )

            return {
                "success": True,
                "count": len(events),
                "search_summary": search_summary,
                "events": events,
            }

        except Exception as e:
            return self.handle_error(e)

    # ─────────────────────────────────────────────────────────
    # LOCATION RESOLUTION
    # ─────────────────────────────────────────────────────────

    def _resolve_location(self, city, state_code, country_code):
        """Fall back to user profile location if city/state not provided."""
        if city and state_code:
            return city, state_code, country_code

        if self.location_service is not None:
            try:
                # Try ContextManager first (has profile data)
                if callable(getattr(self.location_service, "get_location", None)):
                    loc = self.location_service.get_location()
                    if loc and isinstance(loc, dict):
                        city = city or loc.get("city") or ""
                        state = loc.get("state", "")
                        # Normalise full state name → 2-letter code
                        state_code = state_code or self._state_to_code(state) or state[:2].upper()
                        country_code = loc.get("country_code") or country_code
                        if city:
                            logger.info(
                                f"[EventsTool] Using profile location: {city}, {state_code}"
                            )
                            return city, state_code, country_code

                # Fallback to LocationService
                if callable(getattr(self.location_service, "get_current_location", None)):
                    client_ip = getattr(self.location_service, "_client_ip", None)
                    loc = (
                        self.location_service.get_current_location(client_ip=client_ip)
                        if client_ip
                        else self.location_service.get_current_location()
                    )
                    if loc and isinstance(loc, dict):
                        city = city or loc.get("city") or ""
                        state = loc.get("state", "") or loc.get("region", "")
                        state_code = state_code or self._state_to_code(state) or state[:2].upper()
                        if city:
                            return city, state_code, country_code

            except Exception as e:
                logger.warning(f"[EventsTool] Could not resolve location from service: {e}")

        # Last resort defaults
        city = city or "Erie"
        state_code = state_code or "PA"
        return city, state_code, country_code

    # ─────────────────────────────────────────────────────────
    # TICKETMASTER API CALL
    # ─────────────────────────────────────────────────────────

    def _fetch_events(
        self,
        city,
        state_code,
        country_code,
        start_dt,
        end_dt,
        keyword=None,
        segment_id=None,
        page_size=20,
    ) -> list:
        """Call Ticketmaster Discovery API v2 and return raw event list."""
        params = {
            "apikey":        self.api_key,
            "countryCode":   country_code,
            "city":          city,
            "sort":          "date,asc",       # soonest first
            "startDateTime": start_dt,
            "endDateTime":   end_dt,
            "size":          str(page_size),
            "page":          "0",
        }

        if state_code:
            params["stateCode"] = state_code
        if keyword:
            params["keyword"] = keyword
        if segment_id:
            params["segmentId"] = segment_id

        url = "https://app.ticketmaster.com/discovery/v2/events.json?" + urllib.parse.urlencode(params)
        logger.debug(f"[EventsTool] Fetching: {url.replace(self.api_key, '***')}")

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "PersonalizedAgenticAssistant/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        # Ticketmaster wraps results in _embedded.events
        embedded = data.get("_embedded", {})
        events = embedded.get("events", [])
        total = data.get("page", {}).get("totalElements", 0)

        logger.info(
            f"[EventsTool] API returned {len(events)} events "
            f"(total available: {total}) for {city}, {state_code}"
        )
        return events

    # ─────────────────────────────────────────────────────────
    # PARSE & FORMAT
    # ─────────────────────────────────────────────────────────

    def _parse_events(self, raw_events: list) -> list:
        """Extract and format the fields we care about from raw API response."""
        events = []

        for ev in raw_events:
            try:
                name = ev.get("name", "Unknown Event")
                url  = ev.get("url", "")

                # Date / time
                dates     = ev.get("dates", {})
                start     = dates.get("start", {})
                date_str  = start.get("localDate", "")       # "2026-04-05"
                time_str  = start.get("localTime", "")       # "19:00:00"
                tbd       = start.get("dateTBD", False) or start.get("timeTBD", False)

                # Format for display
                display_date = self._format_date(date_str, time_str, tbd)

                # Venue
                venues     = ev.get("_embedded", {}).get("venues", [])
                venue_name = venues[0].get("name", "Venue TBD") if venues else "Venue TBD"
                venue_city = ""
                venue_addr = ""
                if venues:
                    v = venues[0]
                    city_d  = v.get("city",    {}).get("name", "")
                    state_d = v.get("state",   {}).get("stateCode", "")
                    venue_city = f"{city_d}, {state_d}" if city_d and state_d else city_d
                    street = v.get("address", {}).get("line1", "")
                    venue_addr = f"{street}, {venue_city}" if street else venue_city

                # Category / genre
                classifications = ev.get("classifications", [{}])
                segment = classifications[0].get("segment", {}).get("name", "")
                genre   = classifications[0].get("genre",   {}).get("name", "")
                category = " › ".join(p for p in [segment, genre] if p and p != "Undefined")

                # Price range
                price_ranges = ev.get("priceRanges", [])
                price_str = ""
                if price_ranges:
                    pr = price_ranges[0]
                    lo = pr.get("min")
                    hi = pr.get("max")
                    curr = pr.get("currency", "USD")
                    if lo and hi:
                        price_str = f"${lo:.0f} – ${hi:.0f} {curr}"
                    elif lo:
                        price_str = f"From ${lo:.0f} {curr}"

                # Image (highest-res)
                images = ev.get("images", [])
                image_url = ""
                if images:
                    best = max(images, key=lambda i: i.get("width", 0) * i.get("height", 0))
                    image_url = best.get("url", "")

                # Status
                status = ev.get("dates", {}).get("status", {}).get("code", "")

                events.append({
                    "name":       name,
                    "date":       display_date,
                    "date_raw":   date_str,           # for sorting
                    "venue":      venue_name,
                    "address":    venue_addr,
                    "category":   category,
                    "price":      price_str or "See website",
                    "status":     status,
                    "url":        url,
                    "image_url":  image_url,
                })

            except Exception as e:
                logger.debug(f"[EventsTool] Skipping malformed event: {e}")
                continue

        # Sort by soonest date (API already returns date,asc but re-sort to be safe)
        events.sort(key=lambda e: e.get("date_raw") or "9999-99-99")

        # Remove the raw sort key before returning
        for ev in events:
            ev.pop("date_raw", None)

        return events

    # ─────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _format_date(date_str: str, time_str: str, tbd: bool) -> str:
        """Convert API date/time strings to a human-readable format."""
        if not date_str:
            return "Date TBD"
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day = dt.strftime("%A, %B %-d, %Y")   # e.g. "Saturday, April 5, 2026"
        except Exception:
            day = date_str

        if tbd or not time_str:
            return f"{day} — Time TBD"

        try:
            t = datetime.strptime(time_str, "%H:%M:%S")
            return f"{day} at {t.strftime('%-I:%M %p')}"   # "at 7:00 PM"
        except Exception:
            return day

    @staticmethod
    def _state_to_code(state_name: str) -> str:
        """Convert full US state name to 2-letter abbreviation."""
        STATE_MAP = {
            "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
            "california": "CA", "colorado": "CO", "connecticut": "CT",
            "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI",
            "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
            "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
            "maryland": "MD", "massachusetts": "MA", "michigan": "MI",
            "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
            "montana": "MT", "nebraska": "NE", "nevada": "NV",
            "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
            "new york": "NY", "north carolina": "NC", "north dakota": "ND",
            "ohio": "OH", "oklahoma": "OK", "oregon": "OR",
            "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
            "south dakota": "SD", "tennessee": "TN", "texas": "TX",
            "utah": "UT", "vermont": "VT", "virginia": "VA",
            "washington": "WA", "west virginia": "WV", "wisconsin": "WI",
            "wyoming": "WY", "district of columbia": "DC",
        }
        return STATE_MAP.get(state_name.lower().strip(), "")
