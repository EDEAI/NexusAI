/*
 * @LastEditors: biz
 */
import useSocketStore from '@/store/websocket';
import { useWebSocket } from 'ahooks';

// const URL = {
//     chat: 'ws://192.168.4.80:8765/',
//     dealt: 'ws://192.168.4.80:9474/ws',
// };
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
                // console.log('Received message', message, listen);
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
    };
};

export default useWebSocketManager;
