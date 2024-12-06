/*
 * @LastEditors: biz
 */
import { defineConfig } from '@umijs/max';
import { join } from 'path';
import defaultSettings from './defaultSettings';
import envConfig from './envConfig';
import proxy from './proxy';
import routes from './routes';

const { REACT_APP_ENV = 'dev' } = process.env;
const myEnvVar = process.env;

const prevConfig = envConfig[REACT_APP_ENV as keyof typeof envConfig];
const contConfig = {
    API_URL: myEnvVar.WEB_API_URL || prevConfig.API_URL,
    WS_URL: myEnvVar.WEB_WS_URL || prevConfig.WS_URL,
    CHAT_URL: myEnvVar.WEB_CHAT_URL || prevConfig.CHAT_URL,
    OUTPUT_PATH: myEnvVar.WEB_OUTPUT_PATH || prevConfig.OUTPUT_PATH,
};
// const contConfig = prevConfig
export default defineConfig({
    extraPostCSSPlugins: [require('tailwindcss'), require('autoprefixer')],
    define: {
        ...contConfig,
    },
    outputPath: envConfig[REACT_APP_ENV as keyof typeof envConfig].OUTPUT_PATH,
    hash: true,
    clickToComponent: {},
    conventionRoutes: {
        exclude: [/\/.history\//],
    },
    routes,
    theme: {
        'root-entry-name': 'variable',
    },
    ignoreMomentLocale: true,
    proxy: proxy[REACT_APP_ENV as keyof typeof proxy],
    fastRefresh: true,
    model: {},
    initialState: {},
    title: 'Nexus Ai',
    layout: {
        locale: true,
        ...defaultSettings,
    },
    moment2dayjs: {
        preset: 'antd',
        plugins: ['duration'],
    },
    locale: {
        default: 'en-US',
        antd: true,
        baseNavigator: true,
    },
    antd: {},
    request: {},
    access: {},
    headScripts: [
        { src: '/scripts/loading.js', async: false },
    ],
    presets: ['umi-presets-pro'],
    openAPI: [
        {
            requestLibPath: "import { request } from '@umijs/max'",
            schemaPath: join(__dirname, 'oneapi.json'),
            mock: false,
        },
        {
            requestLibPath: "import { request } from '@umijs/max'",
            schemaPath: 'https://gw.alipayobjects.com/os/antfincdn/CA1dOm%2631B/openapi.json',
            projectName: 'swagger',
        },
    ],
    mfsu: {
        strategy: 'normal',
    },
    esbuildMinifyIIFE: true,
    requestRecord: {},
});
