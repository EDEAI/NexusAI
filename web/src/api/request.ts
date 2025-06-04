/*
 * @LastEditors: biz
 */
/*
 * @LastEditors: biz
 */

export namespace REQ_TYPE {
    export interface ApiResponse<T = any> {
        detail: string;
        code: number;
        message: string;
        data: T;
        access_token?: string;
    }
}

import { request, RequestConfig } from '@umijs/max';
import { LOGIN_URL } from '.';
export const BASE_URL = API_URL;
// export const BASE_URL = 'http://192.168.4.80:9472';
const DEFAULT_CONTENT_TYPE = 'application/json; charset=UTF-8';

const apiRequest = async <T>(
    url: string,
    options: RequestConfig,
): Promise<REQ_TYPE.ApiResponse<T>> => {
    let { method = 'POST', headers = {}, data = {} } = options;
    headers['Accept'] = headers['Accept'] || 'application/json';
    headers['Content-Type'] = headers['Content-Type'] || DEFAULT_CONTENT_TYPE;
    let requestData = method.toUpperCase() === 'GET' ? { params: data } : { data };
    const token = localStorage.getItem('token');
   

    if (token && url !== LOGIN_URL) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return request(url, {
        baseURL: BASE_URL,
        method,
        headers,
        ...requestData,
    });
};

export default apiRequest;

// export const aniRequest = <T>(url: string, options: RequestConfig) => {
//     return umiUseRequest<REQ_TYPE.ApiResponse<T>>(() => apiRequest<T>(url, options));
// };
