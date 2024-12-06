import { AvatarDropdown, AvatarName, Footer, SelectLang } from '@/components';
import type { Settings as LayoutSettings } from '@ant-design/pro-components';
import type { RunTimeLayoutConfig } from '@umijs/max';
import { history } from '@umijs/max';
import { useMount } from 'ahooks';
import { useState } from 'react';
import defaultSettings from '../config/defaultSettings';
import Header from './components/Header';
import useSaveWorkFlow from './components/WorkFlow/saveWorkFlow';
import useStore from './components/WorkFlow/store';
import { useResetPanel } from './hooks/useResetPanel';
import useWebSocketManager from './hooks/useSocket';
import PageWrap from './layout';
import { errorConfig } from './requestErrorConfig';
const isDev = process.env.NODE_ENV === 'development';
const loginPath = '/user/login';

if(!localStorage.getItem('umi_locale')){
    localStorage.setItem('umi_locale','en-US');
}
/**
 * @see  https://umijs.org/zh-CN/plugins/plugin-initial-state
 * */
export async function getInitialState(): Promise<{
    settings?: Partial<LayoutSettings>;
    currentUser?: API.CurrentUser;
    loading?: boolean;
    fetchUserInfo?: () => Promise<API.CurrentUser | undefined>;
}> {

    return {
        // fetchUserInfo,
        settings: defaultSettings as Partial<LayoutSettings>,
    };
}


export const layout: RunTimeLayoutConfig = ({ initialState, setInitialState }) => {
    const nodes = useStore(state => state.nodes);
    const { location } = history;
    const [lastRouter, setLastRouter] = useState(location.pathname);
    const saveWorkFlow = useSaveWorkFlow();
    const resetPanel = useResetPanel();
    return {
        actionsRender: () => [<SelectLang key="SelectLang" />],
        avatarProps: {
            src: '/logo.svg',
            title: <AvatarName />,
            render: (_, avatarChildren) => {
                console.log('avatarChildren', avatarChildren);

                return <AvatarDropdown>{avatarChildren}</AvatarDropdown>;
            },
        },
        // waterMarkProps: {
        //   content: 'admin',
        // },
        headerRender: () => <Header></Header>,

        footerRender: () => <Footer />,
        onPageChange: (...args) => {
            if (lastRouter == '/workspace/workflow' && args[0]?.pathname != '/workspace/workflow') {
                saveWorkFlow();
            }

            setLastRouter(args[0].pathname);
            const { location } = history;
            console.log('nodes', nodes);
            resetPanel();
            const token = localStorage.getItem('token');
            if (token) {
                return;
            }
            if (location.pathname !== loginPath) {
                history.push(loginPath);
            }
        },


        menuHeaderRender: undefined,

        // unAccessible: <div>unAccessible</div>,

        childrenRender: children => {
            // if (initialState?.loading) return <PageLoading />;
            const { runSocket } = useWebSocketManager('dealt');
            useMount(() => {
                runSocket();
            });
            return (
                <div>
                    <PageWrap key={location.pathname}>{children}</PageWrap>

                </div>
            );
        },
        ...initialState?.settings,
    };
};


export const request = {
    ...errorConfig,
};
