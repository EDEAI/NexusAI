/*
 * @LastEditors: biz
 */
export default {
    test: {
        '/api/': {
            target: 'https://proapi.azurewebsites.net',
            changeOrigin: true,
            pathRewrite: { '^': '' },
        },
    },
    pre: {
        '/api/': {
            target: 'your pre url',
            changeOrigin: true,
            pathRewrite: { '^': '' },
        },
    },
};
