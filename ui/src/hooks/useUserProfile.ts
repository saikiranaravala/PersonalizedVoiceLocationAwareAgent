/**
 * User Profile Hook
 * Manages user profile and preferences with local storage persistence
 */

import { useState, useEffect, useCallback } from 'react';
import {
  UserProfile,
  UserPreferences,
  UserData,
  RestaurantVisit,
  UberTrip,
  getTitle,
  getFullNameWithTitle,
  generateGreeting,
} from '../types/userProfile';

const STORAGE_KEY = 'voice_assistant_user_data';

/**
 * Default user preferences
 */
const getDefaultPreferences = (): UserPreferences => ({
  favoriteRestaurants: [],
  uberTrips: [],
  preferredCuisines: [],
  dietaryRestrictions: [],
  enablePersonalizedGreeting: true,
  enableActivityTracking: true,
  lastActivityDate: new Date(),
});

/**
 * Hook for managing user profile and preferences
 */
export function useUserProfile() {
  const [userData, setUserData] = useState<UserData | null>(null);
  const [isProfileSetup, setIsProfileSetup] = useState(false);

  /**
   * Load user data from local storage
   */
  useEffect(() => {
    const loadUserData = () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const parsed = JSON.parse(stored);
          
          // Convert date strings back to Date objects
          if (parsed.profile) {
            parsed.profile.createdAt = new Date(parsed.profile.createdAt);
            parsed.profile.lastUpdatedAt = new Date(parsed.profile.lastUpdatedAt);
          }
          
          if (parsed.preferences) {
            parsed.preferences.lastActivityDate = new Date(parsed.preferences.lastActivityDate);
            
            // Convert restaurant visit dates
            parsed.preferences.favoriteRestaurants = parsed.preferences.favoriteRestaurants.map(
              (visit: any) => ({
                ...visit,
                visitedAt: new Date(visit.visitedAt),
              })
            );
            
            // Convert uber trip dates
            parsed.preferences.uberTrips = parsed.preferences.uberTrips.map(
              (trip: any) => ({
                ...trip,
                tripDate: new Date(trip.tripDate),
              })
            );
          }
          
          setUserData(parsed);
          setIsProfileSetup(true);
          console.log('[User Profile] Loaded user data:', parsed);
        } else {
          console.log('[User Profile] No existing user data found');
          setIsProfileSetup(false);
        }
      } catch (error) {
        console.error('[User Profile] Failed to load user data:', error);
        setIsProfileSetup(false);
      }
    };

    loadUserData();
  }, []);

  /**
   * Save user data to local storage
   */
  const saveUserData = useCallback((data: UserData) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      setUserData(data);
      console.log('[User Profile] Saved user data');
    } catch (error) {
      console.error('[User Profile] Failed to save user data:', error);
    }
  }, []);

  /**
   * Create or update user profile
   */
  const updateProfile = useCallback((profile: Partial<UserProfile>) => {
    const now = new Date();
    
    if (userData) {
      // Update existing profile
      const updatedProfile: UserProfile = {
        ...userData.profile,
        ...profile,
        lastUpdatedAt: now,
      };
      
      // Update title if gender or age changed
      if (profile.gender || profile.age !== undefined) {
        updatedProfile.title = getTitle(
          updatedProfile.gender,
          updatedProfile.age,
          profile.title
        );
      }
      
      saveUserData({
        ...userData,
        profile: updatedProfile,
      });
    } else {
      // Create new profile
      const newProfile: UserProfile = {
        id: `user_${Date.now()}`,
        firstName: profile.firstName || 'User',
        lastName: profile.lastName,
        gender: profile.gender || 'prefer-not-to-say',
        age: profile.age,
        title: profile.title || getTitle(profile.gender || 'prefer-not-to-say', profile.age),
        address: profile.address,  // ← was missing: address not saved on first setup
        city: profile.city || 'Erie',
        state: profile.state || 'Pennsylvania',
        country: profile.country || 'US',
        createdAt: now,
        lastUpdatedAt: now,
      };
      
      saveUserData({
        profile: newProfile,
        preferences: getDefaultPreferences(),
      });
      setIsProfileSetup(true);
    }
  }, [userData, saveUserData]);

  /**
   * Add restaurant visit
   */
  const addRestaurantVisit = useCallback((visit: Omit<RestaurantVisit, 'id' | 'visitedAt'>) => {
    if (!userData) return;

    const newVisit: RestaurantVisit = {
      ...visit,
      id: `restaurant_${Date.now()}`,
      visitedAt: new Date(),
    };

    const updatedPreferences: UserPreferences = {
      ...userData.preferences,
      favoriteRestaurants: [newVisit, ...userData.preferences.favoriteRestaurants],
      lastActivityDate: new Date(),
    };

    // Update preferred cuisines
    if (visit.cuisine && !updatedPreferences.preferredCuisines.includes(visit.cuisine)) {
      updatedPreferences.preferredCuisines.push(visit.cuisine);
    }

    saveUserData({
      ...userData,
      preferences: updatedPreferences,
    });

    console.log('[User Profile] Added restaurant visit:', newVisit);
  }, [userData, saveUserData]);

  /**
   * Add Uber trip
   */
  const addUberTrip = useCallback((trip: Omit<UberTrip, 'id' | 'tripDate'>) => {
    if (!userData) return;

    const newTrip: UberTrip = {
      ...trip,
      id: `uber_${Date.now()}`,
      tripDate: new Date(),
    };

    const updatedPreferences: UserPreferences = {
      ...userData.preferences,
      uberTrips: [newTrip, ...userData.preferences.uberTrips],
      lastActivityDate: new Date(),
    };

    saveUserData({
      ...userData,
      preferences: updatedPreferences,
    });

    console.log('[User Profile] Added Uber trip:', newTrip);
  }, [userData, saveUserData]);

  /**
   * Get personalized greeting
   */
  const getGreeting = useCallback((): string => {
    if (!userData || !userData.preferences.enablePersonalizedGreeting) {
      return 'Hello! How can I help you today?';
    }

    return generateGreeting(userData.profile);
  }, [userData]);

  /**
   * Get user's favorite restaurants
   */
  const getFavoriteRestaurants = useCallback((limit?: number): RestaurantVisit[] => {
    if (!userData) return [];
    
    const restaurants = userData.preferences.favoriteRestaurants;
    return limit ? restaurants.slice(0, limit) : restaurants;
  }, [userData]);

  /**
   * Get frequently visited places (from Uber trips)
   */
  const getFrequentDestinations = useCallback((limit: number = 5): string[] => {
    if (!userData) return [];

    const destinations = userData.preferences.uberTrips.reduce((acc, trip) => {
      acc[trip.destination] = (acc[trip.destination] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(destinations)
      .sort(([, a], [, b]) => b - a)
      .slice(0, limit)
      .map(([dest]) => dest);
  }, [userData]);

  /**
   * Get user context for LLM
   */
  const getUserContext = useCallback((): string => {
    if (!userData) return '';

    const context = [
      `User: ${getFullNameWithTitle(userData.profile)}`,
      `Location: ${userData.profile.city}, ${userData.profile.state}`,
    ];

    if (userData.preferences.preferredCuisines.length > 0) {
      context.push(`Preferred cuisines: ${userData.preferences.preferredCuisines.join(', ')}`);
    }

    if (userData.preferences.dietaryRestrictions.length > 0) {
      context.push(`Dietary restrictions: ${userData.preferences.dietaryRestrictions.join(', ')}`);
    }

    const recentRestaurants = getFavoriteRestaurants(3);
    if (recentRestaurants.length > 0) {
      context.push(
        `Recent restaurants: ${recentRestaurants.map(r => r.name).join(', ')}`
      );
    }

    const frequentDestinations = getFrequentDestinations(3);
    if (frequentDestinations.length > 0) {
      context.push(`Frequent destinations: ${frequentDestinations.join(', ')}`);
    }

    return context.join('\n');
  }, [userData, getFavoriteRestaurants, getFrequentDestinations]);

  /**
   * Reset user data (for testing or privacy)
   */
  const resetUserData = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setUserData(null);
    setIsProfileSetup(false);
    console.log('[User Profile] Reset user data');
  }, []);

  return {
    // State
    userData,
    isProfileSetup,
    profile: userData?.profile,
    preferences: userData?.preferences,

    // Actions
    updateProfile,
    addRestaurantVisit,
    addUberTrip,
    resetUserData,

    // Getters
    getGreeting,
    getFullName: () => userData ? getFullNameWithTitle(userData.profile) : '',
    getFavoriteRestaurants,
    getFrequentDestinations,
    getUserContext,
  };
}
