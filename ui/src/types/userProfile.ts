/**
 * User Profile and Preferences Types
 */

export type Gender = 'male' | 'female' | 'other' | 'prefer-not-to-say';
export type AgeGroup = 'child' | 'teen' | 'adult' | 'senior';
export type Title = 'Mr.' | 'Mrs.' | 'Ms.' | 'Miss' | 'Dr.' | 'Master' | '';

export interface UserProfile {
  // Basic Info
  id: string;
  firstName: string;
  lastName?: string;
  gender: Gender;
  age?: number;
  title: Title;
  
  // Location
  city: string;
  state: string;
  country: string;
  
  // Metadata
  createdAt: Date;
  lastUpdatedAt: Date;
}

export interface RestaurantVisit {
  id: string;
  name: string;
  address: string;
  cuisine: string;
  visitedAt: Date;
  rating?: number;
  notes?: string;
}

export interface UberTrip {
  id: string;
  destination: string;
  destinationAddress: string;
  tripDate: Date;
  purpose?: string; // 'restaurant', 'shopping', 'work', 'other'
}

export interface UserPreferences {
  // Favorite Restaurants
  favoriteRestaurants: RestaurantVisit[];
  
  // Uber Trips History
  uberTrips: UberTrip[];
  
  // Preferences
  preferredCuisines: string[];
  dietaryRestrictions: string[];
  
  // App Settings
  enablePersonalizedGreeting: boolean;
  enableActivityTracking: boolean;
  
  // Metadata
  lastActivityDate: Date;
}

export interface UserData {
  profile: UserProfile;
  preferences: UserPreferences;
}

/**
 * Helper function to determine title based on gender and age
 */
export function getTitle(gender: Gender, age?: number, customTitle?: Title): Title {
  if (customTitle && customTitle !== '') return customTitle;
  
  if (gender === 'male') {
    if (age && age < 18) return 'Master';
    return 'Mr.';
  } else if (gender === 'female') {
    if (age && age < 18) return 'Miss';
    // Default to Ms. as it's neutral
    return 'Ms.';
  }
  
  return '';
}

/**
 * Helper function to get full name with title
 */
export function getFullNameWithTitle(profile: UserProfile): string {
  const title = profile.title || getTitle(profile.gender, profile.age);
  const lastName = profile.lastName || profile.firstName;
  return `${title} ${lastName}`.trim();
}

/**
 * Helper function to generate personalized greeting
 */
export function generateGreeting(profile: UserProfile): string {
  const fullName = getFullNameWithTitle(profile);
  const timeOfDay = getTimeOfDay();
  
  const greetings = [
    `${timeOfDay}, ${fullName}! How is ${profile.city}, ${profile.state} treating you? How can I help you today?`,
    `Hello ${fullName}! Welcome back! What can I do for you in ${profile.city} today?`,
    `${timeOfDay}, ${fullName}! Ready to explore ${profile.city}? What would you like to do?`,
    `Hey ${fullName}! Great to see you! How can I assist you in ${profile.city} today?`,
  ];
  
  // Rotate through greetings based on day
  const index = new Date().getDate() % greetings.length;
  return greetings[index];
}

/**
 * Get time of day for greeting
 */
function getTimeOfDay(): string {
  const hour = new Date().getHours();
  
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

/**
 * Get age group from age
 */
export function getAgeGroup(age: number): AgeGroup {
  if (age < 13) return 'child';
  if (age < 18) return 'teen';
  if (age < 60) return 'adult';
  return 'senior';
}
