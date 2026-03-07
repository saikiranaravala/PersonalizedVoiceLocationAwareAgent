# 🎯 Smart Pickup Location Detection

## Feature Overview

The Uber tool now intelligently determines the pickup location based on:
1. **Device type** (mobile vs desktop)
2. **User profile** settings
3. **Current GPS** location

---

## 🎨 How It Works

### Mobile Devices (Smartphones, Tablets)
```
User opens app on iPhone/Android
    ↓
System detects: "Mobile device"
    ↓
Pickup = Current GPS location (always)
    ↓
"📍 Pickup: Current Location"
```

**Examples:**
- iPhone Safari → GPS location
- Android Chrome → GPS location
- iPad → GPS location

### Desktop Devices (Laptops, PCs)
```
User opens app on Desktop
    ↓
System detects: "Desktop device"
    ↓
Check user profile:
    Has address? → Use profile address
    No address?  → Use system location
    ↓
"📍 Pickup: Your Home" or "📍 Pickup: Erie, PA"
```

**Examples:**
- Chrome on Mac → Profile address (if set)
- Firefox on Windows → Profile address (if set)
- Edge on PC → System location (if no profile)

---

## 📱 Detection Logic

### 1. Device Detection

**Mobile indicators:**
```
User-Agent contains:
- "Mobile"
- "Android"
- "iPhone", "iPad", "iPod"
- "Windows Phone"
- "Blackberry"
- etc.
```

**Desktop:**
```
User-Agent contains:
- "Mozilla" (without mobile)
- "Chrome" (desktop)
- "Safari" (desktop)
- "Edge"
- etc.
```

### 2. Pickup Source Priority

```python
if explicit_pickup_provided:
    use_explicit_pickup()  # User specified
elif is_mobile_device():
    use_current_gps()  # Always for mobile
elif user_profile_has_address():
    use_profile_address()  # Desktop with profile
else:
    use_system_location()  # Desktop fallback
```

---

## 🧪 Testing

### Test 1: Mobile Device

```bash
# Simulate mobile request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)" \
  -d '{"message": "Book ride to 5013 Burgundy Dr"}'

# Expected logs:
[INFO] Mobile device detected - using GPS location: Erie, Pennsylvania, US
[INFO] Generated Uber link: Erie, Pennsylvania, US (gps) → 5013 Burgundy Dr

# Expected response:
"Uber ride from your current location to 5013 Burgundy Dr"
"✅ Pickup: Erie, Pennsylvania, US (Current Location)"
```

### Test 2: Desktop with Profile

```bash
# Simulate desktop with user profile
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0" \
  -d '{
    "message": "Book ride to 5013 Burgundy Dr",
    "user_profile": {"address": "123 Main St, Erie, PA"}
  }'

# Expected logs:
[INFO] Desktop - using profile address: 123 Main St, Erie, PA
[INFO] Generated Uber link: 123 Main St, Erie, PA (profile) → 5013 Burgundy Dr

# Expected response:
"Uber ride from your home (123 Main St, Erie, PA) to 5013 Burgundy Dr"
"✅ Pickup: 123 Main St, Erie, PA (Your Home)"
```

### Test 3: Desktop without Profile

```bash
# Simulate desktop without profile
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  -d '{"message": "Book ride to 5013 Burgundy Dr"}'

# Expected logs:
[INFO] Desktop - no profile address, using system location: Erie, Pennsylvania, US
[INFO] Generated Uber link: Erie, Pennsylvania, US (system) → 5013 Burgundy Dr

# Expected response:
"Uber ride from Erie, Pennsylvania, US to 5013 Burgundy Dr"
"✅ Pickup: Erie, Pennsylvania, US (Default Location)"
```

---

## 📊 Pickup Sources

| Source | When Used | Label | Example |
|--------|-----------|-------|---------|
| **gps** | Mobile devices | "Current Location" | iPhone user |
| **profile** | Desktop with profile address | "Your Home" | Desktop + profile set |
| **system** | Desktop without profile | "Default Location" | Desktop + no profile |
| **explicit** | User specifies pickup | "Specified" | "From airport to hotel" |
| **system_fallback** | Profile geocoding fails | "Default Location" | Invalid profile address |

---

## 🎯 User Experience

### Mobile User:
```
📱 Opens app on iPhone
🗣️ "Book a ride to the mall"
🤖 "Uber ride from your current location to Erie Mall"
🔗 Click link
📍 Pickup: [GPS coordinates] ✅
📍 Dropoff: Erie Mall ✅
✅ Ride booked!
```

### Desktop User with Profile:
```
💻 Opens app on laptop
👤 Profile has: "123 Main St, Erie, PA"
🗣️ "Book a ride to the mall"
🤖 "Uber ride from your home (123 Main St) to Erie Mall"
🔗 Click link
📍 Pickup: 123 Main St ✅
📍 Dropoff: Erie Mall ✅
✅ Ride booked!
```

### Desktop User without Profile:
```
💻 Opens app on laptop
👤 No profile address set
🗣️ "Book a ride to the mall"
🤖 "Uber ride from Erie, PA to Erie Mall"
🔗 Click link
📍 Pickup: Erie, PA (default) ✅
📍 Dropoff: Erie Mall ✅
✅ Ride booked!
```

---

## 🔧 Implementation Details

### Files Modified:

**1. `src/utils/device_detection.py` (NEW)**
```python
def is_mobile_device(user_agent: str) -> bool:
    # Detects mobile devices

def get_device_type(user_agent: str) -> str:
    # Returns: 'mobile', 'tablet', or 'desktop'

def should_use_gps(user_agent: str) -> bool:
    # True for mobile, False for desktop
```

**2. `src/tools/uber.py` (UPDATED)**
```python
def execute(self, destination, pickup=None, 
            user_agent=None, user_profile=None):
    # Smart pickup detection logic
    
def _format_message(self, pickup, destination, source):
    # User-friendly messages

def _get_source_label(self, source):
    # Source labels for UI
```

**3. `src/agent/core.py` (UPDATED)**
```python
def process_request(self, user_input, user_agent=None, 
                   user_profile=None):
    # Accepts context
    
# Wrapper for Uber tool with context
def uber_execute_with_context(...):
    # Injects user_agent and user_profile
```

---

## 📝 User Profile Structure

```json
{
  "address": "123 Main St, Erie, PA 16509",
  "name": "John Doe",
  "preferences": {
    "favorite_destinations": [...]
  }
}
```

**Required for pickup:**
- `address`: Full address string

**Optional:**
- Other profile fields for personalization

---

## 🚀 Quick Start

```bash
# 1. Extract package
tar -xzf personalized-agentic-assistant-smart-pickup.tar.gz
cd personalized-agentic-assistant

# 2. Restart backend
python api_server.py

# 3. Test mobile (use mobile browser or user-agent)
# Opens from phone → Uses GPS automatically

# 4. Test desktop without profile
# Opens from computer → Uses system location

# 5. Test desktop with profile
# Set profile address in UI → Uses home address
```

---

## 🎨 Response Messages

### Mobile:
```
"Uber ride from your current location to 5013 Burgundy Dr"
"✅ Pickup: Current Location"
```

### Desktop with Profile:
```
"Uber ride from your home (123 Main St, Erie, PA) to 5013 Burgundy Dr"
"✅ Pickup: 123 Main St, Erie, PA (Your Home)"
```

### Desktop without Profile:
```
"Uber ride from Erie, Pennsylvania, US to 5013 Burgundy Dr"
"✅ Pickup: Erie, Pennsylvania, US (Default Location)"
```

### Explicit Pickup:
```
"Uber ride from Airport to Downtown Hotel"
"✅ Pickup: Airport (Specified)"
```

---

## ✅ Benefits

1. **Mobile Users**: Always get current GPS location (most accurate)
2. **Desktop Users**: Convenient home address from profile
3. **Fallback**: System location works without any setup
4. **Flexibility**: Can still specify custom pickup
5. **Smart**: Automatic detection, no manual selection needed

---

## 🔍 Troubleshooting

### Mobile not detecting GPS:
```
Check: User-Agent header contains mobile indicators
Check: Location services enabled
Check: Browser permissions for location
```

### Profile address not working:
```
Check: Profile has 'address' field
Check: Address is valid and geocodable
Check: Desktop user-agent (not mobile)
```

### Always using system location:
```
Check: Profile address is set correctly
Check: Not on mobile device
Check: Address geocoding succeeds
```

---

**Smart pickup detection is now live!** 🎉

Mobile devices automatically use GPS, desktop uses your profile address, and there's always a fallback. No manual selection needed!
