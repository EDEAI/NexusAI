/*
 * @LastEditors: biz
 */

// Import custom API request method
import apiRequest from './request';

// Define login parameter interface to standardize the parameters needed for login
interface LoginParamsType {
    username: string; // Username
    password: string; // Password
}

// Define the URL for the login interface
export const LOGIN_URL = '/v1/auth/login';
export const USERINFO_URL = '/v1/auth/user_info';

// Define URLs for forgot password flow
export const SEND_EMAIL_VERIFICATION_CODE_URL = '/v1/auth/send_email_verification_code';
export const VERIFY_EMAIL_CODE_URL = '/v1/auth/verify_email_code';
export const RESET_PASSWORD_URL = '/v1/auth/reset_password';

/**
 * Login function, performs login operation using the provided username and password
 * @param data Login parameter object, containing username and password
 * @returns Returns a Promise, which resolves to a boolean indicating whether the login was successful
 */
export const login = async (data: LoginParamsType) => {
    // Create form data object
    const formData = new FormData();
    // Add username and password to the form data
    formData.append('username', data.username);
    formData.append('password', data.password);

    // Initiate login request and handle response
    const res = await apiRequest<any>(LOGIN_URL, {
        method: 'POST',
        data: formData,
        headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' },
    });
    if (res?.access_token) {
        localStorage.setItem('token', res.access_token);
    }
    return res;
};

// Get user information
export const userinfo = async () => {
    const res = await apiRequest<any>(USERINFO_URL, {
        method: 'GET',
    });
    return res;
};

/**
 * Direct login function for development environment, uses hardcoded username and password
 * @returns Returns a Promise, which resolves to a boolean indicating whether the login was successful
 */
export const devLogin = () => {
    // Use fixed username and password to call the login function
    // return login({ username: '13011112222', password: '123456' });
};

// Forgot password flow interfaces
interface SendEmailVerificationCodeParams {
    email: string;
}

interface VerifyEmailCodeParams {
    email: string;
    verification_code: string;
}

interface ResetPasswordParams {
    email: string;
    password: string;
    confirm_password: string;
}

/**
 * Send verification code for forgot password
 * @param data Email address to send verification code
 * @returns Returns a Promise with API response
 */
export const send_email_verification_code = async (data: SendEmailVerificationCodeParams) => {
    const res = await apiRequest<any>(SEND_EMAIL_VERIFICATION_CODE_URL, {
        method: 'POST',
        data,
    });
    return res;
};

/**
 * Verify verification code for forgot password
 * @param data Email and verification code
 * @returns Returns a Promise with API response
 */
export const verify_email_code = async (data: VerifyEmailCodeParams) => {
    const res = await apiRequest<any>(VERIFY_EMAIL_CODE_URL, {
        method: 'POST',
        data,
    });
    return res;
};

/**
 * Reset password using verification code
 * @param data Email, password and confirm password
 * @returns Returns a Promise with API response
 */
export const reset_password = async (data: ResetPasswordParams) => {
    const res = await apiRequest<any>(RESET_PASSWORD_URL, {
        method: 'POST',
        data,
    });
    return res;
};

// Update user profile
export const updateProfile = async (data: { nickname: string; position?: string }) => {
    const res = await apiRequest<any>('/v1/auth/update_profile', {
        method: 'POST',
        data,
    });
    return res;
};

// Change password
export const changePassword = async (data: { 
    old_password: string; 
    new_password: string; 
    confirm_password: string; 
}) => {
    const res = await apiRequest<any>('/v1/auth/change_password', {
        method: 'POST',
        data,
    });
    return res;
};

// Role management related interfaces
export const ROLES_URL = '/v1/roles/';
export const ROLES_PERMISSION_LIST_URL = '/v1/roles/permission_list';
export const ROLES_CREATE_URL = '/v1/roles/create_role';
export const ROLES_UPDATE_URL = '/v1/roles/update_role';
export const ROLES_DETAIL_URL = '/v1/roles/role_detail';

// Define role related interfaces
interface Role {
    id: number;
    name: string;
    description: string;
    status: number;
    created_at: string;
    updated_at: string | null;
}

interface Permission {
    id: number;
    title: string;
}

interface RoleDetail {
    id: number;
    name: string;
    description: string;
    permissions: Permission[];
}

interface RoleListResponse {
    list: Role[];
    total_count: number;
    total_pages: number;
    page: number;
    page_size: number;
}

interface PermissionListResponse {
    list: Permission[];
    total_count: number;
    total_pages: number;
    page: number;
    page_size: number;
}

interface CreateRoleParams {
    name: string;
    description: string;
    list: number[]; // Permission IDs
}

interface UpdateRoleParams {
    id: number;
    name: string;
    description: string;
    list: number[]; // Permission IDs
}

/**
 * Get roles list
 * @param params Query parameters
 * @returns Promise with roles list response
 */
export const getRolesList = async (params?: { page?: number; page_size?: number; status?: number }) => {
    const res = await apiRequest<RoleListResponse>(ROLES_URL, {
        method: 'GET',
        data: params || {},
    });
    return res;
};

/**
 * Get permissions list
 * @returns Promise with permissions list response
 */
export const getPermissionsList = async () => {
    const res = await apiRequest<PermissionListResponse>(ROLES_PERMISSION_LIST_URL, {
        method: 'GET',
        data: { page: 1, page_size: 20, status: 2 },
    });
    return res;
};

/**
 * Create new role
 * @param data Role creation parameters
 * @returns Promise with creation response
 */
export const createRole = async (data: CreateRoleParams) => {
    const res = await apiRequest<any>(ROLES_CREATE_URL, {
        method: 'POST',
        data,
    });
    return res;
};

/**
 * Update existing role
 * @param data Role update parameters
 * @returns Promise with update response
 */
export const updateRole = async (data: UpdateRoleParams) => {
    const res = await apiRequest<any>(`${ROLES_UPDATE_URL}/${data.id}`, {
        method: 'PUT',
        data,
    });
    return res;
};

/**
 * Delete role by ID
 * @param roleId Role ID to delete
 * @returns Promise with deletion response
 */
export const deleteRole = async (roleId: number) => {
    const res = await apiRequest<any>(`${ROLES_URL}${roleId}`, {
        method: 'DELETE',
    });
    return res;
};

/**
 * Get role detail by ID
 * @param roleId Role ID to get detail
 * @returns Promise with role detail response
 */
export const getRoleDetail = async (roleId: number) => {
    const res = await apiRequest<RoleDetail>(`${ROLES_DETAIL_URL}/${roleId}`, {
        method: 'GET',
    });
    return res;
};