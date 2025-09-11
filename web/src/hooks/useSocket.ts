/*
 * @LastEditors: biz
 */
import useSocketStore from '@/store/websocket';
import { checkViewInIframe, getIframeApiUrl, getIframeChatWsUrl, getIframeHostName, getProtocolIsHttps } from '@/utils/fullscreenStorage';
import { useLatest, useWebSocket } from 'ahooks';
import { useEffect, useRef } from 'react';

const URL = {
    chat: CHAT_URL,
    dealt: WS_URL,
};
type ManagerType = 'chat' | 'dealt';

const useWebSocketManager = (type: ManagerType = 'dealt', listen?: Function) => {
    let url = URL[type];
    if(checkViewInIframe()){
        url = getIframeChatWsUrl();
    }
    const addFlowMessage = useSocketStore(state => state.addFlowMessage);
    const timerRef = useRef<NodeJS.Timeout>();

    let wsUrl= `${url}?token=${localStorage.getItem('token')}`

    if(checkViewInIframe()){
        wsUrl = wsUrl+ `&chat_base_url=${getIframeApiUrl()}`
    }

    const { readyState, sendMessage, latestMessage, disconnect, connect } = useWebSocket(
       wsUrl,
        {
            reconnectInterval: 1000,
            reconnectLimit: 10,
            manual: true,
            onOpen: () => {},
            onMessage: message => {
                listen && listen(message);
                if (type == 'dealt') {
                    try {
                        const data = JSON.parse(message.data);
                        addFlowMessage(data);
                    } catch (e) {
                        console.error('WebSocket format conversion error', message.data, e);
                    }
                }
            },
        },
    );
    const lastReadyState=useLatest(readyState)

    const checkAndConnect = () => {
        if (lastReadyState.current !== 1&&lastReadyState.current !== 0) {
            console.debug('Socket not connected, attempting to connect...:lastReadyState',lastReadyState.current);
            connect();
            return false;
        }
        return true;
    };

    const startTimer = () => {
        if (timerRef.current) return;
        timerRef.current = setInterval(() => {
            checkAndConnect();
        }, 10000);
    };

    const runSocket = () => {
        console.debug('Socket reconnected');
        connect();
        startTimer();
    };

    useEffect(() => {
        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
                timerRef.current = undefined;
            }
            disconnect();
        };
    }, []);

    return {
        readyState,
        sendMessage,
        disconnect,
        connect,
        runSocket,
        checkAndConnect,
    };
};

export default useWebSocketManager;
