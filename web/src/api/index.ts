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