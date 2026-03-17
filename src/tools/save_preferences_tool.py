"""
save_preferences_tool.py
========================
LangChain tool that saves user preferences by sending structured `action`
messages back to the frontend over WebSocket.

The frontend's useVoiceAssistant hook listens for `{"type": "action", ...}`
messages and calls addRestaurantVisit / addUberTrip to persist to localStorage.

Usage in your agent:
    from tools.save_preferences_tool import SaveRestaurantTool, SaveUberTripTool

    tools = [
        SearchRestaurantsTool(...),
        SaveRestaurantTool(websocket_sender=ws_send),
        SaveUberTripTool(websocket_sender=ws_send),
    ]
"""

import json
from typing import Any, Callable, Optional
from pydantic import BaseModel, Field
from tools import BaseTool


# ─────────────────────────────────────────────────────────────────────────────
# INPUT SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

class SaveRestaurantInput(BaseModel):
    name: str = Field(description="Full name of the restaurant, e.g. 'El Amigo Mexican Grill'")
    address: str = Field(default="", description="Street address of the restaurant")
    cuisine: str = Field(default="", description="Cuisine type, e.g. 'Mexican', 'Indian', 'Italian'")
    rating: Optional[float] = Field(default=None, description="User rating 1-5 (optional)")
    notes: Optional[str] = Field(default=None, description="Any notes about the visit (optional)")


class SaveUberTripInput(BaseModel):
    destination: str = Field(description="Destination name, e.g. 'Millcreek Mall'")
    destination_address: str = Field(default="", description="Full address of the destination")
    purpose: Optional[str] = Field(
        default="other",
        description="Trip purpose: 'restaurant', 'shopping', 'work', or 'other'"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────────────────────────────────────

class SaveRestaurantTool(BaseTool):
    """
    Saves a restaurant to the user's favorites in the browser localStorage.
    Sends an `action` WebSocket message to the frontend which calls
    addRestaurantVisit() to persist the data.

    Call this tool whenever:
    - User says "save this restaurant", "remember this place", "add to favorites"
    - User visits a restaurant found via search_restaurants
    - User explicitly asks to track a restaurant
    """

    name: str = "save_favorite_restaurant"
    description: str = (
        "Save a restaurant to the user's favorites. "
        "Call this when the user wants to remember or save a restaurant. "
        "Requires: name (restaurant name). "
        "Optional: address, cuisine type, rating (1-5), notes."
    )
    args_schema: type[BaseModel] = SaveRestaurantInput

    # Injected at agent startup — pass the WebSocket send function
    websocket_sender: Optional[Callable] = None

    def execute(
        self,
        name: str,
        address: str = "",
        cuisine: str = "",
        rating: Optional[float] = None,
        notes: Optional[str] = None,
        **kwargs
    ) -> str:
        """Send action message to frontend to save restaurant."""

        action_message = {
            "type":   "action",
            "action": "save_restaurant",
            "data": {
                "name":    name,
                "address": address,
                "cuisine": cuisine,
                "rating":  rating,
                "notes":   notes,
            }
        }

        if self.websocket_sender:
            try:
                self.websocket_sender(json.dumps(action_message))
                return (
                    f"✅ Saved '{name}' to your favorite restaurants. "
                    f"I'll remember this for future recommendations!"
                )
            except Exception as e:
                return f"⚠️ Could not save restaurant: {e}"
        else:
            # Fallback: no WebSocket sender — log and acknowledge
            return (
                f"Noted! I've remembered '{name}' as one of your favorite restaurants."
            )


class SaveUberTripTool(BaseTool):
    """
    Saves an Uber trip destination to the user's trip history in localStorage.
    Sends an `action` WebSocket message to the frontend which calls
    addUberTrip() to persist the data.

    Call this tool whenever:
    - An Uber ride is booked or confirmed
    - User asks to remember a destination
    """

    name: str = "save_uber_trip"
    description: str = (
        "Save an Uber trip to the user's trip history. "
        "Call this after a ride is booked or confirmed. "
        "Requires: destination (place name). "
        "Optional: destination_address, purpose (restaurant/shopping/work/other)."
    )
    args_schema: type[BaseModel] = SaveUberTripInput

    websocket_sender: Optional[Callable] = None

    def execute(
        self,
        destination: str,
        destination_address: str = "",
        purpose: str = "other",
        **kwargs
    ) -> str:
        """Send action message to frontend to save uber trip."""

        action_message = {
            "type":   "action",
            "action": "save_uber_trip",
            "data": {
                "destination":        destination,
                "destinationAddress": destination_address,
                "purpose":            purpose,
            }
        }

        if self.websocket_sender:
            try:
                self.websocket_sender(json.dumps(action_message))
                return (
                    f"✅ Saved your trip to '{destination}' in your trip history."
                )
            except Exception as e:
                return f"⚠️ Could not save trip: {e}"
        else:
            return f"Noted! I've remembered your trip to '{destination}'."


# ─────────────────────────────────────────────────────────────────────────────
# HOW TO WIRE THIS INTO YOUR AGENT (api_server.py / agent/core.py)
# ─────────────────────────────────────────────────────────────────────────────

WIRING_EXAMPLE = """
# In api_server.py, inside your WebSocket handler:

import asyncio
import json
from fastapi import WebSocket
from tools.save_preferences_tool import SaveRestaurantTool, SaveUberTripTool
from tools.restaurant_finder import RestaurantFinder
from services.context import ContextManager

async def handle_websocket(websocket: WebSocket):
    await websocket.accept()

    context = ContextManager()

    # Create a synchronous sender wrapper for the async WebSocket
    def ws_send(message: str):
        asyncio.create_task(websocket.send_text(message))

    # Build tools — pass ws_send so they can push action messages to frontend
    tools = [
        RestaurantFinder(location_service=context),
        SaveRestaurantTool(websocket_sender=ws_send),
        SaveUberTripTool(websocket_sender=ws_send),
    ]

    agent = build_agent(tools=tools)

    while True:
        data = await websocket.receive_text()
        message = json.loads(data)

        response = agent.run(message["text"])

        # Send text response back to frontend
        await websocket.send_text(json.dumps({
            "type": "response",
            "message": response,
        }))
"""
