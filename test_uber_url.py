#!/usr/bin/env python3
"""
Test script to generate and verify Uber deep links.
Run this to see the exact URL that will be generated.
"""

from urllib.parse import quote

def generate_uber_link(pickup_name, pickup_lat, pickup_lon, dest_name, dest_lat, dest_lon):
    """Generate Uber deep link with given coordinates."""
    
    # URL-encode addresses
    pickup_encoded = quote(pickup_name, safe='')
    dest_encoded = quote(dest_name, safe='')
    
    # Version 1: With generic client_id (recommended)
    deep_link = (
        f"https://m.uber.com/ul/"
        f"?client_id=web_deeplink"  # Generic identifier, works for anyone
        f"&action=setPickup"
        f"&pickup[latitude]={pickup_lat}"
        f"&pickup[longitude]={pickup_lon}"
        f"&pickup[formatted_address]={pickup_encoded}"
        f"&pickup[nickname]={pickup_encoded}"
        f"&dropoff[latitude]={dest_lat}"
        f"&dropoff[longitude]={dest_lon}"
        f"&dropoff[formatted_address]={dest_encoded}"
        f"&dropoff[nickname]={dest_encoded}"
    )
    
    # Version 2: Without client_id (fallback)
    simple_link = (
        f"https://m.uber.com/ul/"
        f"?action=setPickup"
        f"&pickup[latitude]={pickup_lat}"
        f"&pickup[longitude]={pickup_lon}"
        f"&pickup[formatted_address]={pickup_encoded}"
        f"&dropoff[latitude]={dest_lat}"
        f"&dropoff[longitude]={dest_lon}"
        f"&dropoff[formatted_address]={dest_encoded}"
    )
    
    return deep_link, simple_link


# Test Case 1: Erie, PA to Olive Garden
print("=" * 80)
print("TEST CASE 1: Erie, PA to Olive Garden")
print("=" * 80)

pickup = "Erie, Pennsylvania, US"
pickup_lat = 42.1292
pickup_lon = -80.0851

destination = "5945 Peach St, Erie, PA 16509"
dest_lat = 42.068388
dest_lon = -80.120485

url, simple_url = generate_uber_link(pickup, pickup_lat, pickup_lon, destination, dest_lat, dest_lon)
print(f"\nPickup: {pickup}")
print(f"Coordinates: ({pickup_lat}, {pickup_lon})")
print(f"\nDestination: {destination}")
print(f"Coordinates: ({dest_lat}, {dest_lon})")
print(f"\n🔗 VERSION 1 (With client_id - Recommended):")
print(url)
print(f"\n🔗 VERSION 2 (Without client_id - Fallback):")
print(simple_url)
print(f"\n✅ Try BOTH URLs in your browser")
print(f"✅ Both should pre-fill pickup and dropoff")

# Test Case 2: Different example
print("\n" + "=" * 80)
print("TEST CASE 2: New York to JFK Airport")
print("=" * 80)

pickup2 = "Times Square, New York, NY"
pickup_lat2 = 40.7580
pickup_lon2 = -73.9855

destination2 = "JFK Airport, Queens, NY"
dest_lat2 = 40.6413
dest_lon2 = -73.7781

url2, simple_url2 = generate_uber_link(pickup2, pickup_lat2, pickup_lon2, destination2, dest_lat2, dest_lon2)
print(f"\nPickup: {pickup2}")
print(f"Destination: {destination2}")
print(f"\n🔗 VERSION 1 (With client_id):")
print(url2)
print(f"\n🔗 VERSION 2 (Without client_id):")
print(simple_url2)

print("\n" + "=" * 80)
print("TESTING INSTRUCTIONS:")
print("=" * 80)
print("""
TWO VERSIONS PROVIDED:

Version 1: With client_id="web_deeplink"
  - No registration needed
  - "web_deeplink" is a generic identifier that works for anyone
  - Recommended for better compatibility

Version 2: Without client_id  
  - Simpler URL
  - May work on some Uber versions
  - Fallback if Version 1 has issues

TEST BOTH:
1. Copy Version 1 URL
2. Paste it in your browser
3. Uber should open with:
   - Pickup location PRE-FILLED ✅
   - Dropoff location PRE-FILLED ✅
   - Map showing both pins ✅

4. If Version 1 doesn't work, try Version 2

NOTE: "client_id" doesn't need to be registered with Uber for deep links.
It's just an identifier. "web_deeplink" works for anyone!
""")
