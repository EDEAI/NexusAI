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