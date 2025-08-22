// Permission utility functions for checking user permissions

interface Permission {
  id: number;
  title: string;
  status: number;
  created_at?: string;
  updated_at?: string;
}

interface UserInfo {
  permissions?: Permission[];
  role?: number;
  [key: string]: any;
}

/**
 * Check if user has specific permission by permission ID
 * @param userInfo - User information containing permissions array
 * @param permissionId - Permission ID to check
 * @returns boolean - true if user has the permission
 */
export const hasPermission = (userInfo: UserInfo | null, permissionId: number): boolean => {
  if (!userInfo || !userInfo.permissions) {
    return false;
  }

  // Team admin (role === 1) has all permissions
  if (userInfo.role === 1) {
    return true;
  }

  // Check if user has the specific permission
  return userInfo.permissions.some(permission => 
    permission.id === permissionId && permission.status === 1
  );
};

/**
 * Check if user has any of the specified permissions
 * @param userInfo - User information containing permissions array
 * @param permissionIds - Array of permission IDs to check
 * @returns boolean - true if user has any of the permissions
 */
export const hasAnyPermission = (userInfo: UserInfo | null, permissionIds: number[]): boolean => {
  if (!userInfo || !userInfo.permissions) {
    return false;
  }

  // Team admin (role === 1) has all permissions
  if (userInfo.role === 1) {
    return true;
  }

  // Check if user has any of the specified permissions
  return permissionIds.some(permissionId => 
    userInfo.permissions!.some(permission => 
      permission.id === permissionId && permission.status === 1
    )
  );
};

/**
 * Check if user has all of the specified permissions
 * @param userInfo - User information containing permissions array
 * @param permissionIds - Array of permission IDs to check
 * @returns boolean - true if user has all of the permissions
 */
export const hasAllPermissions = (userInfo: UserInfo | null, permissionIds: number[]): boolean => {
  if (!userInfo || !userInfo.permissions) {
    return false;
  }

  // Team admin (role === 1) has all permissions
  if (userInfo.role === 1) {
    return true;
  }

  // Check if user has all of the specified permissions
  return permissionIds.every(permissionId => 
    userInfo.permissions!.some(permission => 
      permission.id === permissionId && permission.status === 1
    )
  );
};

/**
 * Check if user is team admin
 * @param userInfo - User information
 * @returns boolean - true if user is team admin
 */
export const isTeamAdmin = (userInfo: UserInfo | null): boolean => {
  return userInfo?.role === 1;
};

/**
 * Get user's permission IDs
 * @param userInfo - User information containing permissions array
 * @returns number[] - Array of permission IDs
 */
export const getUserPermissionIds = (userInfo: UserInfo | null): number[] => {
  if (!userInfo || !userInfo.permissions) {
    return [];
  }

  return userInfo.permissions
    .filter(permission => permission.status === 1)
    .map(permission => permission.id);
};

// Common permission IDs (these should match the actual permission IDs in your database)
export const PERMISSION_IDS = {
  // Agent permissions
  CREATE_AGENT: 1,
  
  // Workflow permissions
  CREATE_WORKFLOW: 2,
  
  // Knowledge base permissions
  CREATE_KNOWLEDGE_BASE: 5,
  
  // Meeting permissions
  CREATE_MEETING: 4,
  
  // Skill permissions
  CREATE_SKILL: 3,
} as const;

// Type for permission ID values
export type PermissionId = typeof PERMISSION_IDS[keyof typeof PERMISSION_IDS];