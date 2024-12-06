/*
 * @LastEditors: biz
 */
module.exports = {
    extends: [require.resolve('@umijs/lint/dist/config/eslint')],
    globals: {
        page: true,
        REACT_APP_ENV: true,
    },
    rules: {
        'prettier/prettier': [
            'error',
            {
                tabWidth: 4,
            },
        ],
        indent: ['error', 4],
    },
};
