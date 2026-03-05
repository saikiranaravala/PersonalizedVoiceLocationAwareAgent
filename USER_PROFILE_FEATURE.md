# 👤 User Profile & Preferences System

## Overview

The Voice Assistant now includes a comprehensive **User Profile and Preferences** system that personalizes the entire experience based on who you are, where you live, and your past interactions.

###

 Key Features:

✅ **Personalized Greetings** - "Good morning, Mr. Jack! How is Erie, PA treating you?"
✅ **User Profile** - Name, gender, age, location
✅ **Activity Tracking** - Remembers restaurant visits and Uber trips
✅ **Smart Recommendations** - Based on your history and preferences
✅ **Proper Titles** - Mr., Mrs., Ms., Miss, Dr., Master (auto or custom)
✅ **Persistent Storage** - All data saved locally in browser
✅ **Privacy First** - Your data never leaves your device

---

## 🎯 Personalized Greetings

The assistant now greets you by name with context about your location:

### Examples:

**For Mr. Jack in Erie, PA:**
```
"Good morning, Mr. Jack! How is Erie, PA treating you? How can I help you today?"
```

**For Miss Nancy in New York:**
```
"Hello Miss Nancy! Welcome back! What can I do for you in New York today?"
```

**For Mrs. Jackson in Boston:**
```
"Good afternoon, Mrs. Jackson! Ready to explore Boston? What would you like to do?"
```

**For Master David (child) in Chicago:**
```
"Hey Master David! Great to see you! How can I assist you in Chicago today?"
```

### Greeting Variations:

The system rotates through 4 different greeting styles based on the day to keep things fresh:

1. **Time-based + Location**: "Good [morning/afternoon/evening], [Title Name]! How is [City], [State] treating you?"
2. **Welcome back**: "Hello [Title Name]! Welcome back! What can I do for you in [City] today?"
3. **Ready to explore**: "[Time], [Title Name]! Ready to explore [City]? What would you like to do?"
4. **Great to see you**: "Hey [Title Name]! Great to see you! How can I assist you in [City] today?"

---

## 📋 User Profile Setup

### First Time Setup

When you first open the app, you'll see a 3-step profile setup wizard:

#### **Step 1: What's your name?**
```
┌────────────────────────────────────┐
│ Welcome! Let's Get to Know You     │
│ This helps me provide personalized │
│ assistance                          │
│                                    │
│ Progress: Step 1 of 3              │
├────────────────────────────────────┤
│ What's your name?                  │
│                                    │
│ First Name *                       │
│ [Jack                        ]     │
│                                    │
│ Last Name (Optional)               │
│ [Smith                       ]     │
│                                    │
│           [Skip for now]  [Next]   │
└────────────────────────────────────┘
```

#### **Step 2: A few more details**
```
┌────────────────────────────────────┐
│ Progress: Step 2 of 3              │
├────────────────────────────────────┤
│ A few more details                 │
│                                    │
│ Gender                             │
│ [Male                       ▼]     │
│                                    │
│ Age (Optional)                     │
│ [35                          ]     │
│                                    │
│ Title (Optional)                   │
│ [Auto (based on gender/age) ▼]     │
│                                    │
│            [Back]         [Next]   │
└────────────────────────────────────┘
```

#### **Step 3: Where are you located?**
```
┌────────────────────────────────────┐
│ Progress: Step 3 of 3              │
├────────────────────────────────────┤
│ Where are you located?             │
│                                    │
│ City *                             │
│ [Erie                        ]     │
│                                    │
│ State/Province                     │
│ [Pennsylvania                ]     │
│                                    │
│ Country                            │
│ [US                          ]     │
│                                    │
│ ℹ️  This helps me provide location │
│     -specific recommendations      │
│                                    │
│          [Back]  [Complete Setup]  │
└────────────────────────────────────┘
```

###  Profile Fields:

| Field | Type | Required | Auto-Generated | Notes |
|-------|------|----------|----------------|-------|
| **First Name** | Text | ✅ Yes | ❌ No | Used in greetings |
| **Last Name** | Text | ❌ No | ❌ No | Used for formal address |
| **Gender** | Select | ❌ No | ❌ No | Used for title determination |
| **Age** | Number | ❌ No | ❌ No | Used for title (Master for <18) |
| **Title** | Select | ❌ No | ✅ Yes | Auto or manual |
| **City** | Text | ✅ Yes | ❌ No | For location-based services |
| **State** | Text | ❌ No | ❌ No | Full location context |
| **Country** | Text | ❌ No | ❌ No | International support |

---

## 🎭 Title System

### Automatic Title Assignment:

The system automatically assigns appropriate titles based on gender and age:

| Gender | Age | Auto Title |
|--------|-----|-----------|
| Male | < 18 | **Master** |
| Male | ≥ 18 | **Mr.** |
| Female | < 18 | **Miss** |
| Female | ≥ 18 | **Ms.** |
| Other | Any | *None* |
| Prefer not to say | Any | *None* |

### Manual Title Override:

You can choose your own title regardless of gender/age:
- **Mr.** - Male (adult)
- **Mrs.** - Married female
- **Ms.** - Female (neutral)
- **Miss** - Female (young/unmarried)
- **Dr.** - Doctorate holder
- **Master** - Male child

### Examples:

```typescript
// Auto-assigned
{ firstName: "Jack", gender: "male", age: 35 }
→ "Mr. Jack"

{ firstName: "Nancy", gender: "female", age: 16 }
→ "Miss Nancy"

{ firstName: "David", gender: "male", age: 10 }
→ "Master David"

// Manual override
{ firstName: "Jackson", gender: "female", title: "Mrs." }
→ "Mrs. Jackson"

{ firstName: "Smith", gender: "male", title: "Dr." }
→ "Dr. Smith"
```

---

## 📊 Activity Tracking

The system automatically tracks your interactions to provide better recommendations:

### 1. Restaurant Visits

**What's Tracked:**
```typescript
interface RestaurantVisit {
  name: string;           // "Luigi's Italian Kitchen"
  address: string;        // "200 Demo St, Erie, PA"
  cuisine: string;        // "Italian"
  visitedAt: Date;        // 2026-03-05 14:30:00
  rating?: number;        // 5 (1-5 stars)
  notes?: string;         // "Great carbonara!"
}
```

**How It's Used:**
- Remember your favorite restaurants
- Learn cuisine preferences (Italian, Chinese, Mexican, etc.)
- Provide personalized recommendations
- "You've been to Luigi's 3 times - want to try something new?"

**Example Tracking:**
```
User: "Find Italian restaurants"
Assistant: "I found 5 Italian places. By the way, you loved Luigi's 
last week - want to go back there?"
```

### 2. Uber Trips

**What's Tracked:**
```typescript
interface UberTrip {
  destination: string;          // "Luigi's Italian Kitchen"
  destinationAddress: string;   // "200 Demo St, Erie, PA"
  tripDate: Date;               // 2026-03-05 19:00:00
  purpose?: string;             // "restaurant", "work", "shopping", "other"
}
```

**How It's Used:**
- Remember frequently visited places
- Quick-book to favorite destinations
- Understand your patterns
- "Heading to work? I'll book your usual route."

**Example Tracking:**
```
User: "Book me a ride"
Assistant: "Where to? Your frequent destinations are:
1. Luigi's Restaurant (5 times)
2. Downtown Office (12 times)
3. Erie Mall (3 times)"
```

### 3. Cuisine Preferences

**Auto-Learned:**
- Tracks which cuisines you search for
- Records restaurant visits by type
- Builds preference profile

**Examples:**
```json
{
  "preferredCuisines": [
    "Italian",      // Visited 5 times
    "Mexican",      // Visited 3 times
    "Chinese"       // Visited 2 times
  ]
}
```

**Usage:**
```
User: "Find me a restaurant"
Assistant: "Based on your preferences, here are some Italian places 
(your favorite!). Want to try something different?"
```

---

## 💾 Data Storage

### Local Storage Only

**Privacy-First Design:**
- ✅ All data stored in browser's `localStorage`
- ✅ Never sent to external servers
- ✅ Completely under your control
- ✅ Can be deleted anytime

**Storage Key:**
```
voice_assistant_user_data
```

**Data Structure:**
```json
{
  "profile": {
    "id": "user_1709683200000",
    "firstName": "Jack",
    "lastName": "Smith",
    "gender": "male",
    "age": 35,
    "title": "Mr.",
    "city": "Erie",
    "state": "Pennsylvania",
    "country": "US",
    "createdAt": "2026-03-05T10:00:00.000Z",
    "lastUpdatedAt": "2026-03-05T10:00:00.000Z"
  },
  "preferences": {
    "favoriteRestaurants": [
      {
        "id": "restaurant_1709683500000",
        "name": "Luigi's Italian Kitchen",
        "address": "200 Demo St, Erie, PA",
        "cuisine": "Italian",
        "visitedAt": "2026-03-05T14:30:00.000Z",
        "rating": 5,
        "notes": "Great carbonara!"
      }
    ],
    "uberTrips": [
      {
        "id": "uber_1709686800000",
        "destination": "Luigi's Italian Kitchen",
        "destinationAddress": "200 Demo St, Erie, PA",
        "tripDate": "2026-03-05T19:00:00.000Z",
        "purpose": "restaurant"
      }
    ],
    "preferredCuisines": ["Italian", "Mexican"],
    "dietaryRestrictions": [],
    "enablePersonalizedGreeting": true,
    "enableActivityTracking": true,
    "lastActivityDate": "2026-03-05T19:00:00.000Z"
  }
}
```

### Managing Your Data

**View in Browser:**
```javascript
// Open browser console (F12)
localStorage.getItem('voice_assistant_user_data')
```

**Export Your Data:**
```javascript
// Copy to clipboard
const data = localStorage.getItem('voice_assistant_user_data');
navigator.clipboard.writeText(data);
console.log('Data copied to clipboard');
```

**Delete Your Data:**
```javascript
// From browser console
localStorage.removeItem('voice_assistant_user_data');
location.reload();
```

**Or use the app:**
```
Click "Edit Profile" → Reset Data (coming soon)
```

---

## 🎨 User Interface

### Empty State (With Profile):

```
┌────────────────────────────────────────────────┐
│               🎤                               │
│                                                │
│  Good morning, Mr. Jack! How is Erie, PA      │
│  treating you? How can I help you today?      │
│                                                │
│  I can help you with weather, restaurants,    │
│  rides, and more                               │
│                                                │
│            [Edit Profile]                      │
└────────────────────────────────────────────────┘
```

### Empty State (No Profile):

```
┌────────────────────────────────────────────────┐
│               🎤                               │
│                                                │
│       Tap the microphone to start              │
│                                                │
│  I can help you with weather, restaurants,    │
│  rides, and more                               │
└────────────────────────────────────────────────┘
```

---

## 🚀 How to Use

### First Time Setup:

1. **Open the app** - `http://localhost:5173`
2. **Wait 1 second** - Profile setup modal appears automatically
3. **Enter your details** - Follow the 3-step wizard
4. **Click "Complete Setup"** - Profile saved!
5. **See personalized greeting** - "Good morning, Mr. Jack!"

### Editing Your Profile:

1. **Clear conversation** (if any messages)
2. **Click "Edit Profile"** button
3. **Update your details**
4. **Save changes**

### Skipping Setup:

- Click **"Skip for now"** on first step
- You can set up later via "Edit Profile"
- Generic greetings until profile is set

---

## 🧠 Smart Features

### 1. Context-Aware Assistance

The assistant uses your profile to provide better help:

**Without Profile:**
```
User: "Find a restaurant"
Assistant: "Sure! What type of cuisine are you looking for?"
```

**With Profile:**
```
User: "Find a restaurant"
Assistant: "Based on your history, you love Italian food! 
Want to try that new Italian place downtown, or go back to Luigi's?"
```

### 2. Location-Based Services

**Weather:**
```
User: "What's the weather?"
Assistant: "In Erie, PA, it's currently 45°F and cloudy..."
```

**Restaurants:**
```
User: "Find restaurants"
Assistant: "Here are restaurants near you in Erie, PA..."
```

**Uber:**
```
User: "Book a ride"
Assistant: "From Erie, PA to where would you like to go?"
```

### 3. Personalized Recommendations

**Favorite Cuisines:**
```
User: "I'm hungry"
Assistant: "You usually enjoy Italian or Mexican. Want a 
recommendation for either?"
```

**Frequent Destinations:**
```
User: "Book an Uber"
Assistant: "Your top destinations:
1. Work (Downtown Office) - 12 visits
2. Luigi's Restaurant - 5 visits
3. Erie Mall - 3 visits
Which one?"
```

### 4. Time-Appropriate Greetings

**Morning (5 AM - 12 PM):**
```
"Good morning, Mr. Jack!"
```

**Afternoon (12 PM - 5 PM):**
```
"Good afternoon, Mr. Jack!"
```

**Evening (5 PM - 5 AM):**
```
"Good evening, Mr. Jack!"
```

---

## 📱 Mobile Support

The profile system is fully responsive:

### Mobile Profile Setup:

```
┌──────────────────────┐
│ Welcome! Let's Get   │
│ to Know You          │
│                      │
│ Step 1 of 3          │
│ ▓▓▓▓▓░░░             │
├──────────────────────┤
│ What's your name?    │
│                      │
│ First Name *         │
│ [Jack          ]     │
│                      │
│ Last Name            │
│ [Smith         ]     │
│                      │
│ [Skip for now]       │
│ [Next          ]     │
└──────────────────────┘
```

- Touch-optimized inputs
- Large tap targets
- Smooth animations
- Auto-focus on fields

---

## 🔒 Privacy & Security

### What We Store:
- ✅ Name (you provide)
- ✅ Gender (you choose)
- ✅ Age (optional, you provide)
- ✅ Location (you provide)
- ✅ Restaurant visits (you trigger)
- ✅ Uber trips (you book)

### What We DON'T Store:
- ❌ Passwords
- ❌ Payment info
- ❌ Personal IDs
- ❌ Conversation content (cleared on exit)
- ❌ Voice recordings

### Where It's Stored:
- **Location:** Browser `localStorage` only
- **Sent to server:** NO (stays local)
- **Shared:** NO (private to your device)
- **Encrypted:** Browser-level only

### Your Control:
- **View:** Browser console anytime
- **Export:** Copy data to clipboard
- **Delete:** Clear storage anytime
- **Edit:** Update profile anytime

---

## 🎯 Future Enhancements

### Coming Soon:

1. **Dietary Restrictions Tracking**
   - "I'm vegetarian"
   - "I'm allergic to peanuts"
   - Auto-filter recommendations

2. **Favorite Dishes**
   - Remember what you ordered
   - "You loved the carbonara at Luigi's"

3. **Budget Preferences**
   - "$" to "$$$$" restaurants
   - Price-aware recommendations

4. **Time Preferences**
   - "You usually eat dinner at 7 PM"
   - Proactive suggestions

5. **Weather Preferences**
   - "You like outdoor seating when it's sunny"

6. **Multiple Profiles**
   - Family members
   - Switch between profiles

7. **Profile Backup/Sync**
   - Export to file
   - Import from file
   - Cloud sync (opt-in)

---

## 🧪 Testing the Feature

### Test Scenario 1: New User

1. **Clear localStorage:**
   ```javascript
   localStorage.removeItem('voice_assistant_user_data');
   location.reload();
   ```

2. **Expected:**
   - Profile setup modal appears after 1 second
   - Shows "Step 1 of 3"
   - Can fill in details or skip

### Test Scenario 2: Returning User

1. **Setup profile first** (use Test 1)
2. **Refresh page**
3. **Expected:**
   - No setup modal
   - Personalized greeting shows
   - "Edit Profile" button visible

### Test Scenario 3: Title Auto-Assignment

**Test cases:**
```javascript
// Male adult → Mr.
{ firstName: "Jack", gender: "male", age: 35 }

// Female adult → Ms.
{ firstName: "Nancy", gender: "female", age: 25 }

// Male child → Master
{ firstName: "David", gender: "male", age: 12 }

// Female child → Miss
{ firstName: "Emily", gender: "female", age: 14 }
```

### Test Scenario 4: Activity Tracking

1. **Book restaurant via app**
2. **Check localStorage:**
   ```javascript
   JSON.parse(localStorage.getItem('voice_assistant_user_data')).preferences.favoriteRestaurants
   ```
3. **Expected:** New restaurant entry

---

## 📚 API Reference

### useUserProfile Hook

```typescript
const {
  // State
  userData,              // Full user data object
  isProfileSetup,        // Boolean: is profile configured?
  profile,               // UserProfile object
  preferences,           // UserPreferences object

  // Actions
  updateProfile,         // Update profile data
  addRestaurantVisit,    // Track restaurant visit
  addUberTrip,           // Track Uber trip
  resetUserData,         // Delete all data

  // Getters
  getGreeting,           // Get personalized greeting
  getFullName,           // Get "Title LastName"
  getFavoriteRestaurants,  // Get restaurant history
  getFrequentDestinations, // Get common Uber destinations
  getUserContext,        // Get context for LLM
} = useUserProfile();
```

### Example Usage:

```typescript
// Update profile
updateProfile({
  firstName: "Jack",
  lastName: "Smith",
  gender: "male",
  age: 35,
  city: "Erie",
  state: "Pennsylvania",
});

// Add restaurant visit
addRestaurantVisit({
  name: "Luigi's Italian Kitchen",
  address: "200 Demo St",
  cuisine: "Italian",
  rating: 5,
});

// Add Uber trip
addUberTrip({
  destination: "Luigi's Restaurant",
  destinationAddress: "200 Demo St",
  purpose: "restaurant",
});

// Get greeting
const greeting = getGreeting();
// → "Good morning, Mr. Smith! How is Erie, PA treating you?"

// Get context for LLM
const context = getUserContext();
// → "User: Mr. Smith\nLocation: Erie, Pennsylvania\nPreferred cuisines: Italian, Mexican\n..."
```

---

## ✅ Complete Feature List

### Profile Management:
- ✅ 3-step setup wizard
- ✅ Auto title assignment
- ✅ Manual title override
- ✅ Location tracking
- ✅ Edit profile anytime
- ✅ Skip setup option

### Personalization:
- ✅ Personalized greetings
- ✅ Time-aware greetings
- ✅ Location-based context
- ✅ Name with proper title
- ✅ Rotating greeting styles

### Activity Tracking:
- ✅ Restaurant visit history
- ✅ Uber trip history
- ✅ Cuisine preferences (auto-learned)
- ✅ Frequent destinations
- ✅ Visit timestamps

### Data Management:
- ✅ Local storage persistence
- ✅ Privacy-first design
- ✅ Data portability
- ✅ Easy deletion
- ✅ No external sharing

### User Interface:
- ✅ Beautiful setup modal
- ✅ Progress indicator
- ✅ Responsive design
- ✅ Smooth animations
- ✅ Accessibility support

---

**The Voice Assistant is now truly personal!** 🎉

Every interaction is tailored to you - from the greeting to the recommendations. The more you use it, the smarter it gets at understanding your preferences and helping you efficiently.
