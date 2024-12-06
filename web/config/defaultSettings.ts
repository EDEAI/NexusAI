/*
 * @LastEditors: biz
 */
import { ProLayoutProps } from '@ant-design/pro-components';

/**
 * @name
 */
const Settings: ProLayoutProps & {
    pwa?: boolean;
    logo?: string;
} = {
    navTheme: 'light',

    colorPrimary: '#1b64f3',
  
    layout: 'top',
    // contentWidth: 'Fixed',
    fixedHeader: false,
    footerRender: false,
    fixSiderbar: true,
    colorWeak: false,
    title: 'NEXUS AI',
    pwa: true,
    logo: '/logo.svg',
    iconfontUrl: '',
    token: {
      
        //https://procomponents.ant.design/components/layout#%E9%80%9A%E8%BF%87-token-%E4%BF%AE%E6%94%B9%E6%A0%B7%E5%BC%8F
    },
};

export default Settings;
