/*
 * @LastEditors: biz
 */
module.exports = {
    singleQuote: true,
    trailingComma: 'all',
    printWidth: 100,
    tabWidth: 4, //  4
    useTabs: false,
    proseWrap: 'never',
    endOfLine: 'lf',
    overrides: [
        {
            files: '.prettierrc',
            options: {
                parser: 'json',
            },
        },
        {
            files: 'document.ejs',
            options: {
                parser: 'html',
            },
        },
    ],

    arrowParens: 'avoid',
};
