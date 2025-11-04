// Custom hook for managing user permissions

import { useCallback } from 'react';
import { useUserInfo, type UserInfo } from './useUserInfo';
import { 
  hasPermission, 
  hasAnyPermission, 
  hasAllPermissions, 
  isTeamAdmin, 
  getUserPermissionIds,
  type PermissionId 
} from '../utils/permissions';

interface Permission {
  id: number;
  title: string;
  status: number;
  created_at?: string;
  updated_at?: string;
}

interface UsePermissionsReturn {
  userInfo: UserInfo | null;
  loading: boolean;
  error: string | null;
  hasPermission: (permissionId: number) => boolean;
  hasAnyPermission: (permissionIds: number[]) => boolean;
  hasAllPermissions: (permissionIds: number[]) => boolean;
  isTeamAdmin: () => boolean;
  getUserPermissionIds: () => number[];
  refreshUserInfo: (forceRefresh?: boolean) => Promise<UserInfo | undefined>;
}

/**
 * Custom hook for managing user permissions
 * @returns Object containing user info, permission checking functions, and utility methods
 */
export const usePermissions = (): UsePermissionsReturn => {
  const { userInfo, loading, error, refreshUserInfo } = useUserInfo();

  // Permission checking functions
  const checkPermission = useCallback((permissionId: number): boolean => {
    return hasPermission(userInfo, permissionId);
  }, [userInfo]);

  const checkAnyPermission = useCallback((permissionIds: number[]): boolean => {
    return hasAnyPermission(userInfo, permissionIds);
  }, [userInfo]);

  const checkAllPermissions = useCallback((permissionIds: number[]): boolean => {
    return hasAllPermissions(userInfo, permissionIds);
  }, [userInfo]);

  const checkIsTeamAdmin = useCallback((): boolean => {
    return isTeamAdmin(userInfo);
  }, [userInfo]);

  const getPermissionIds = useCallback((): number[] => {
    return getUserPermissionIds(userInfo);
  }, [userInfo]);

  return {
    userInfo,
    loading,
    error,
    hasPermission: checkPermission,
    hasAnyPermission: checkAnyPermission,
    hasAllPermissions: checkAllPermissions,
    isTeamAdmin: checkIsTeamAdmin,
    getUserPermissionIds: getPermissionIds,
    refreshUserInfo,
  };
};

/**
 * Hook for checking specific permission with loading state
 * @param permissionId - Permission ID to check
 * @returns Object containing permission status and loading state
 */
export const usePermissionCheck = (permissionId: number) => {
  const { userInfo, loading, hasPermission } = usePermissions();
  
  return {
    hasPermission: hasPermission(permissionId),
    loading,
    userInfo,
  };
};

/**
 * Hook for checking multiple permissions
 * @param permissionIds - Array of permission IDs to check
 * @param checkType - 'any' to check if user has any permission, 'all' to check if user has all permissions
 * @returns Object containing permission status and loading state
 */
export const useMultiplePermissionCheck = (
  permissionIds: number[], 
  checkType: 'any' | 'all' = 'any'
) => {
  const { userInfo, loading, hasAnyPermission, hasAllPermissions } = usePermissions();
  
  const hasPermissions = checkType === 'any' 
    ? hasAnyPermission(permissionIds)
    : hasAllPermissions(permissionIds);
  
  return {
    hasPermissions,
    loading,
    userInfo,
  };
};
