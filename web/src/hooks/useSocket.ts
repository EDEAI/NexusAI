/*
 * @LastEditors: biz
 */
import useSocketStore from '@/store/websocket';
import { useWebSocket } from 'ahooks';


const URL = {
    chat: CHAT_URL,
    dealt: WS_URL,
};
type ManagerType = 'chat' | 'dealt';
const useWebSocketManager = (type: ManagerType = 'dealt', listen?: Function) => {
    const url = URL[type];
    const addFlowMessage = useSocketStore(state => state.addFlowMessage);
 

    const { readyState, sendMessage, latestMessage, disconnect, connect } = useWebSocket(
        `${url}?token=${localStorage.getItem('token')}`,
        {
            reconnectInterval: 1000,
            reconnectLimit: 10,
            manual: true,
            onOpen: () => {
               
            },
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

    const checkAndConnect = () => {
        if (readyState !== 1) {
            console.debug('Socket not connected, attempting to connect...');
            connect();
            return false;
        }
        return true;
    };

    const runSocket = () => {
        console.debug('Socket reconnected');
        connect();
    };
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
