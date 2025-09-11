import type { RequestOptions } from '@@/plugin-request/request';
import type { RequestConfig } from '@umijs/max';
import { history } from '@umijs/max';
import { message } from 'antd';
import { checkViewInIframe } from './utils/fullscreenStorage';
const loginPath = '/user/login';

enum ErrorCustomCode {
    SILENT = 0,
    WARN_MESSAGE = 422,
    ERROR_MESSAGE = 402,
    NOTIFICATION = 3,
    REDIRECT = 9,
}
enum ErrorCode {
    SILENT = 0,
    WARN_MESSAGE = 422,
    ERROR_MESSAGE = 402,
    LOGIN_EXPIRE = 401,
    NOTIFICATION = 3,
    REDIRECT = 9,
}

interface ResponseStructure {
    code: number;
    data: any;
    detail: string;
}


export const errorConfig: RequestConfig = {

    errorConfig: {

        errorThrower: res => {
            const { code, data, detail } = res as unknown as ResponseStructure;
            if (!code) {
                const error: any = new Error(detail);
                error.name = 'BizError';
                error.info = { code, detail, data };
                throw error;
            }
        },

        errorHandler: (error: any, opts: any) => {
            console.log(error, opts);

            if (opts?.skipErrorHandler) throw error;

            if (error.name === 'BizError') {
                const errorInfo: ResponseStructure | undefined = error.info;
                if (errorInfo) {
                    const { detail, code } = errorInfo;
                    switch (code) {
                        case ErrorCustomCode.SILENT:

                            break;
                        case ErrorCustomCode.WARN_MESSAGE:
                            message.warning(detail);
                            break;
                        case ErrorCustomCode.ERROR_MESSAGE:
                            message.error(detail);
                            break;

                        case ErrorCustomCode.REDIRECT:
                            // TODO: redirect
                            break;
                        default:
                            message.error(detail);
                    }
                }
            } else if (error.response) {

                console.error(error.response);
                const { status, data } = error.response;
                const detail = data?.detail;
                if (!detail) return;
                switch (status) {
                    case ErrorCode.SILENT:
                        break;
                    case ErrorCode.WARN_MESSAGE:
                        message.warning(detail);
                        break;
                    case ErrorCode.ERROR_MESSAGE:
                        message.error(detail);
                        break;
                    case ErrorCode.LOGIN_EXPIRE:
                        localStorage.removeItem('token');
                        const { location } = history;
                        if (location.pathname !== loginPath&&!checkViewInIframe()) {
                            history.push(loginPath);
                        }
                        break;
                    default:
                        message.error(detail);
                }
            } else if (error.request) {

                message.error('None response! Please retry.');
            } else {

                message.error('Request error, please retry.');
            }
        },
    },


    requestInterceptors: [
        (config: RequestOptions) => {

            const url = config?.url?.concat('?token = 123');
            return { ...config, url };
        },
    ],


    responseInterceptors: [
        response => {

            const { data } = response as unknown as ResponseStructure;

            if (data?.success === false) {
                message.error('fail！');
            }
            return response;
        },
    ],
};
