// API namespace type definitions
export namespace API {
    /**
     * Login parameters interface
     */
    export interface LoginParams {
        username: string;
        password: string;
        autoLogin?: boolean;
    }

    /**
     * Login result interface
     */
    export interface LoginResult {
        status?: 'ok' | 'error';
        type?: string;
    }

    /**
     * User info interface
     */
    export interface UserInfo {
        id: number;
        username: string;
        email: string;
        language?: 'en' | 'zh';
        [key: string]: any;
    }
}