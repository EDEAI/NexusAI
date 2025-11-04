import { useState, useEffect, useCallback, useRef } from 'react';
import { userinfo } from '@/api';
import { checkViewInIframe } from '@/utils/fullscreenStorage';
import { syncLocaleWithLanguage } from '@/utils/locale';

export interface UserInfo {
  uid?: string;
  email?: string;
  nickname?: string;
  position?: string;
  language?: string;
  role?: number;
  permissions?: any[];
  [key: string]: any;
}

interface UseUserInfoReturn {
  userInfo: UserInfo | null;
  loading: boolean;
  error: string | null;
  refreshUserInfo: (forceRefresh?: boolean) => Promise<UserInfo | undefined>;
  updateUserInfo: (newUserInfo: Partial<UserInfo>) => void;
}

// Global state to prevent multiple simultaneous requests
let globalUserInfo: UserInfo | null = null;
let globalLoading = false;
let globalError: string | null = null;
let pendingPromise: Promise<UserInfo> | null = null;
let lastFetchTime = 0;
const subscribers = new Set<() => void>();

// Cache configuration
const CACHE_DURATION = 60 * 1000; // 1 minute cache
const MIN_REQUEST_INTERVAL = 1000; // Minimum 1 second between requests

// Enhanced localStorage functions with timestamp
const setUserInfoWithTimestamp = (userInfo: UserInfo) => {
  const cacheData = {
    userInfo,
    timestamp: Date.now()
  };
  localStorage.setItem('userInfoCache', JSON.stringify(cacheData));
};

const getUserInfoWithTimestamp = (): { userInfo: UserInfo | null; isExpired: boolean } => {
  try {
    const cached = localStorage.getItem('userInfoCache');
    if (!cached) {
      return { userInfo: null, isExpired: true };
    }
    
    const cacheData = JSON.parse(cached);
    const now = Date.now();
    const isExpired = (now - cacheData.timestamp) > CACHE_DURATION;
    
    return {
      userInfo: cacheData.userInfo || null,
      isExpired
    };
  } catch (error) {
    console.error('Error reading user info cache:', error);
    return { userInfo: null, isExpired: true };
  }
};

// Notify all subscribers when global state changes
const notifySubscribers = () => {
  subscribers.forEach(callback => callback());
};

// Fetch user info with deduplication and caching
const fetchUserInfoGlobal = async (forceRefresh = false): Promise<UserInfo> => {
  const now = Date.now();
  
  // If there's already a pending request, return it
  if (pendingPromise) {
    return pendingPromise;
  }

  // Check if we should use cached data
  if (!forceRefresh) {
    // When running inside iframe route, avoid triggering userinfo request automatically.
    if (checkViewInIframe()) {
      // Ensure locale stays consistent with whatever we already know.
      if (globalUserInfo) {
        syncLocaleWithLanguage(globalUserInfo.language);
        return globalUserInfo;
      }
      const { userInfo: cachedUserInfo, isExpired } = getUserInfoWithTimestamp();
      if (cachedUserInfo && !isExpired) {
        syncLocaleWithLanguage(cachedUserInfo.language);
        return cachedUserInfo;
      }
      syncLocaleWithLanguage(globalUserInfo?.language);
      return (globalUserInfo ?? {}) as UserInfo;
    }

    // Check if we have recent cached data in memory
    if (globalUserInfo && (now - lastFetchTime) < CACHE_DURATION) {
      syncLocaleWithLanguage(globalUserInfo.language);
      return globalUserInfo;
    }

    // Check if we have cached data in localStorage with timestamp validation
    const { userInfo: cachedUserInfo, isExpired } = getUserInfoWithTimestamp();
    if (cachedUserInfo && !isExpired) {
      // If memory cache is empty but localStorage has valid data, use it
      if (!globalUserInfo) {
        globalUserInfo = cachedUserInfo;
        globalLoading = false;
        globalError = null;
        lastFetchTime = now;
        notifySubscribers();
      }
      syncLocaleWithLanguage(cachedUserInfo.language);
      return cachedUserInfo;
    }
  }

  // Prevent too frequent requests
  if (!forceRefresh && (now - lastFetchTime) < MIN_REQUEST_INTERVAL) {
    if (globalUserInfo) {
      syncLocaleWithLanguage(globalUserInfo.language);
      return globalUserInfo;
    }
  }

  // Set loading state
  globalLoading = true;
  globalError = null;
  notifySubscribers();

  // Create the promise for the API request
  pendingPromise = (async () => {
    try {
      // If current path is Agent_iframe, skip userinfo call
      if (checkViewInIframe()&&!localStorage.getItem('token')) {
        syncLocaleWithLanguage(globalUserInfo?.language);
        return globalUserInfo ?? ({} as UserInfo);
      }
      const response = await userinfo();
      
      if (response.code === 0 && response.data) {
        globalUserInfo = response.data;
        globalError = null;
        lastFetchTime = now; // Update fetch timestamp
        
        // Update localStorage with timestamp
        setUserInfoWithTimestamp(response.data);
        
        // Trigger custom event for components that listen to it
        window.dispatchEvent(new CustomEvent('userInfoUpdated', { 
          detail: { type: 'userInfoUpdated' } 
        }));
        syncLocaleWithLanguage(response.data.language);
        
        return response.data;
      } else {
        throw new Error('Failed to fetch user information');
      }
    } catch (err) {
      globalError = err instanceof Error ? err.message : 'Unknown error occurred';
      throw err;
    } finally {
      globalLoading = false;
      pendingPromise = null;
      notifySubscribers();
    }
  })();

  return pendingPromise;
};

/**
 * Custom hook for managing user information with global state and request deduplication
 * This hook prevents multiple simultaneous requests to the userinfo API
 */
export const useUserInfo = (): UseUserInfoReturn => {
  const [, forceUpdate] = useState({});
  const subscriberRef = useRef<() => void>();

  // Force component re-render when global state changes
  const triggerUpdate = useCallback(() => {
    forceUpdate({});
  }, []);

  useEffect(() => {
    // Subscribe to global state changes
    subscriberRef.current = triggerUpdate;
    subscribers.add(triggerUpdate);

    // Initialize from cache if available
    if (!globalUserInfo && !globalLoading) {
      const { userInfo: cachedUserInfo, isExpired } = getUserInfoWithTimestamp();
      if (cachedUserInfo && !isExpired) {
        // Use cached data if it's still valid
        globalUserInfo = cachedUserInfo;
        lastFetchTime = Date.now();
        syncLocaleWithLanguage(cachedUserInfo.language);
        triggerUpdate();
      } else {
        // Fetch fresh data if no valid cache
        fetchUserInfoGlobal().catch(console.error);
      }
    }

    return () => {
      // Cleanup subscription
      if (subscriberRef.current) {
        subscribers.delete(subscriberRef.current);
      }
    };
  }, [triggerUpdate]);

  const refreshUserInfo = useCallback(async (forceRefresh = true) => {
    try {
      return await fetchUserInfoGlobal(forceRefresh);
    } catch (error) {
      console.error('Failed to refresh user info:', error);
      return undefined;
    }
  }, []);

  const updateUserInfo = useCallback((newUserInfo: Partial<UserInfo>) => {
    if (globalUserInfo) {
      const updatedUserInfo = { ...globalUserInfo, ...newUserInfo };
      globalUserInfo = updatedUserInfo;
      lastFetchTime = Date.now(); // Update timestamp when manually updating
      
      // Update localStorage with timestamp
      setUserInfoWithTimestamp(updatedUserInfo);
      syncLocaleWithLanguage(updatedUserInfo.language);
      
      // Trigger custom event
      window.dispatchEvent(new CustomEvent('userInfoUpdated', { 
        detail: { type: 'userInfoUpdated' } 
      }));
      
      // Notify subscribers
      notifySubscribers();
    }
  }, []);

  return {
    userInfo: globalUserInfo,
    loading: globalLoading,
    error: globalError,
    refreshUserInfo,
    updateUserInfo,
  };
};

/**
 * Hook for checking if user info is available without triggering a fetch
 */
export const useUserInfoStatus = () => {
  const [, forceUpdate] = useState({});
  const subscriberRef = useRef<() => void>();

  const triggerUpdate = useCallback(() => {
    forceUpdate({});
  }, []);

  useEffect(() => {
    subscriberRef.current = triggerUpdate;
    subscribers.add(triggerUpdate);

    return () => {
      if (subscriberRef.current) {
        subscribers.delete(subscriberRef.current);
      }
    };
  }, [triggerUpdate]);

  return {
    hasUserInfo: !!globalUserInfo,
    loading: globalLoading,
    error: globalError,
  };
};

export default useUserInfo;
