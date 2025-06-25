/*
 * @LastEditors: biz
 */
import React, { FC, memo, useEffect, useRef, useState } from 'react';
import { useIntl } from '@umijs/max';
import { useLocation, useParams } from 'umi';
import useWebSocketManager from '@//hooks/useSocket';
import useChatroomStore from '@/store/chatroomstate';
import { useMessageHandler } from './MessageHandler';
import { CurrentMessage } from './CurrentMessage';
import { MCPToolRuntimeData } from '../types/mcp';

interface chatwindowParameters {
    setisEnd?: any;
    messageApi?: any;
    setCurrentMessageContent?: any;
    sendValue?: any;
    agentList?: any;
    scrollDomRef?: any;
    upButtonDom?: any;
    setIsStop?: any;
    setSendValue?: any;
    agentChatRoomId?: any;
    updateMCPTool?: (id: string | number, updates: Partial<MCPToolRuntimeData>) => void;
    getCurrentMessageList?: () => any[];
    mcpTools?: Record<string | number, MCPToolRuntimeData>;
    getMCPTool?: (id: string | number) => MCPToolRuntimeData | null;
    setIsWaitingReply?: (waiting: boolean) => void;
}

export const Chatwindow: FC<chatwindowParameters> = memo(props => {
    const {
        messageApi,
        setCurrentMessageContent,
        sendValue,
        agentList,
        scrollDomRef,
        upButtonDom,
        setIsStop,
        setisEnd,
        setSendValue,
        agentChatRoomId,
        updateMCPTool,
        getCurrentMessageList,
        mcpTools = {},
        getMCPTool = () => null,
        setIsWaitingReply,
    } = props;
    
    const intl = useIntl();
    const { id: urlParamId } = useParams<{ id: string }>();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const searchParamId = searchParams.get('id');
    const id = agentChatRoomId || urlParamId || searchParamId;

    const setDisableInput = useChatroomStore(state => state.setDisableInput);
    const [currentMessage, setCurrentMessage]: any = useState({});
    const chatReturn = useRef(false);
    const agentText = useRef('');

    const { getSocketMessage } = useMessageHandler(
        setDisableInput,
        setIsStop,
        setSendValue,
        messageApi,
        setCurrentMessageContent,
        scrollDomRef,
        upButtonDom,
        agentList,
        setCurrentMessage,
        currentMessage,
        agentText,
        chatReturn,
        updateMCPTool,
        getCurrentMessageList,
        setIsWaitingReply
    );

    const { runSocket, sendMessage, readyState } = useWebSocketManager('chat', getSocketMessage);

    useEffect(() => {
        if (readyState == 1) {
            if (id) {
                sendMessage(JSON.stringify(['ENTER', parseInt(id)]));
            }
        }
    }, [readyState]);

    useEffect(() => {
        if (sendValue) {
            if (readyState == 1) {
                sendMessage(sendValue);
            }
        }
    }, [sendValue]);

    useEffect(() => {
        runSocket();
    }, []);

    return (
        <CurrentMessage
            currentMessage={currentMessage}
            agentChatRoomId={agentChatRoomId}
            intl={intl}
            mcpTools={mcpTools}
            updateMCPTool={updateMCPTool}
            getMCPTool={getMCPTool}
        />
    );
}); 