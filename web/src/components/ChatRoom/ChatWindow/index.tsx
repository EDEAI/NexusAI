/*
 * @LastEditors: biz
 */
import React, { FC, memo, useCallback, useEffect, useRef, useState } from 'react';
import { useIntl } from '@umijs/max';
import { useLocation, useParams } from 'umi';
import useWebSocketManager from '@//hooks/useSocket';
import useChatroomStore from '@/store/chatroomstate';
import { useMessageHandler } from './MessageHandler';
import { CurrentMessage } from './CurrentMessage';
import { MCPToolRuntimeData } from '../types/mcp';
import { prepareHistoryMessageForCurrent } from '../utils';

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
    removeHistoryMessage?: (message: any) => void;
    setCurrentMessageFromHistory?: (message: any) => void;
    setInstruction?: (instruction: any) => void;
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
        removeHistoryMessage,
        setCurrentMessageFromHistory,
        setInstruction,
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

    // Handle setting current message from history
    const handleSetCurrentMessageFromHistory = useCallback((historyMessage: any) => {
        try {
            // Boundary check: validate history message
            if (!historyMessage || typeof historyMessage !== 'object') {
                console.warn('Invalid history message provided:', historyMessage);
                return;
            }

            // Boundary check: ensure it's an agent message
            if (historyMessage.is_agent !== 1) {
                console.warn('Attempted to set non-agent message as current:', historyMessage);
                return;
            }

            const preparedMessage = prepareHistoryMessageForCurrent(
                historyMessage, 
                getMCPTool
            );
            
            // Boundary check: validate prepared message
            if (!preparedMessage) {
                console.warn('Failed to prepare history message:', historyMessage);
                return;
            }
            
            setCurrentMessage(preparedMessage);
            
            // 关键改动：设置为true以允许后续流式文本追加
            chatReturn.current = true;
            
            // 初始化agentText为当前内容，以便正确累积
            agentText.current = preparedMessage.content || '';
            
        } catch (error) {
            console.error('Failed to set current message from history:', error);
        }
    }, [getMCPTool]);

    // Expose the handler to parent component
    useEffect(() => {
        if (setCurrentMessageFromHistory) {
            setCurrentMessageFromHistory(handleSetCurrentMessageFromHistory);
            
        }
    }, [setCurrentMessageFromHistory, handleSetCurrentMessageFromHistory]);

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
        setIsWaitingReply,
        getMCPTool,
        removeHistoryMessage
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
            setInstruction={setInstruction}
        />
    );
}); 