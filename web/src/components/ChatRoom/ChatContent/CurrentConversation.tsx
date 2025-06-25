/*
 * @LastEditors: biz
 */
import React, { FC, memo, useEffect, useState } from 'react';
import { useLocation, useParams } from 'umi';
import { Chatwindow } from '../ChatWindow';
import { MessageItem } from '../MessageDisplay/MessageItem';
import { MCPToolRuntimeData } from '../types/mcp';
import { WaitingReplyIndicator } from './WaitingReplyIndicator';

interface CurrentConversationProps {
    messageApi?: any;
    setUserMessage?: any;
    sendValue?: any;
    agentList?: any;
    scrollDomRef?: any;
    upButtonDom?: any;
    setIsStop?: any;
    setSendValue?: any;
    agentChatRoomId?: any;
    abilitiesList?: any;
    mcpTools?: Record<string | number, MCPToolRuntimeData>;
    updateMCPTool?: (id: string | number, updates: Partial<MCPToolRuntimeData>) => void;
    getMCPTool?: (id: string | number) => MCPToolRuntimeData | null;
    userMessage?: any[];
}

export const CurrentConversation: FC<CurrentConversationProps> = memo(props => {
    const {
        messageApi,
        setUserMessage,
        sendValue,
        agentList,
        scrollDomRef,
        upButtonDom,
        setIsStop,
        setSendValue,
        agentChatRoomId,
        abilitiesList,
        mcpTools,
        updateMCPTool,
        getMCPTool,
        userMessage,
    } = props;

    const [currentMessageContent, setCurrentMessageContent]: any = useState([]);
    const [isEnd, setisEnd] = useState(false);
    const [isWaitingReply, setIsWaitingReply] = useState(false);
    
    const { id: urlParamId } = useParams<{ id: string }>();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const searchParamId = searchParams.get('id');
    // Use URL param id if available, otherwise use search param id
    const id = urlParamId || searchParamId;

    useEffect(() => {
        if (isEnd) {
            setUserMessage((pre: any) => {
                return [...currentMessageContent.reverse(), ...pre];
            });
            setCurrentMessageContent([]);
            setTimeout(() => {
                setisEnd(false);
                scrollDomRef.current.scrollTop = 0;
            }, 200);
        }
    }, [isEnd]);

    return (
        <>
            {currentMessageContent.length ? (
                currentMessageContent.map((item: any, index: any) => (
                    <MessageItem
                        key={index}
                        item={item}
                        index={index}
                        agentChatRoomId={agentChatRoomId}
                        abilitiesList={abilitiesList}
                        messageApi={messageApi}
                        id={id}
                        idName="currentContent"
                        cidName="currentChilContent"
                        mcpTools={mcpTools}
                        updateMCPTool={updateMCPTool}
                        getMCPTool={getMCPTool}
                    />
                ))
            ) : (
                <></>
            )}
            <WaitingReplyIndicator isVisible={isWaitingReply} />
            <Chatwindow
                messageApi={messageApi}
                setCurrentMessageContent={setCurrentMessageContent}
                sendValue={sendValue}
                agentList={agentList}
                scrollDomRef={scrollDomRef}
                upButtonDom={upButtonDom}
                setIsStop={setIsStop}
                setisEnd={setisEnd}
                setSendValue={setSendValue}
                agentChatRoomId={agentChatRoomId}
                updateMCPTool={updateMCPTool}
                getCurrentMessageList={() => userMessage || []}
                mcpTools={mcpTools}
                getMCPTool={getMCPTool}
                setIsWaitingReply={setIsWaitingReply}
            />
        </>
    );
}); 