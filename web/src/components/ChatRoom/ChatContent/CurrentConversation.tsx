/*
 * @LastEditors: biz
 */
import React, { FC, memo, useEffect, useRef, useState } from 'react';
import { useLocation, useParams } from 'umi';
import { Chatwindow } from '../ChatWindow';
import { MessageItem } from '../MessageDisplay/MessageItem';
import { MCPToolRuntimeData } from '../types/mcp';
import { WaitingReplyIndicator } from './WaitingReplyIndicator';
import { checkLastAgentMessage } from '../utils';
import { useChatRoomContext } from '../context/ChatRoomContext';

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
    
    // Use context for setInstruction
    const { setInstruction } = useChatRoomContext();

    const [currentMessageContent, setCurrentMessageContent]: any = useState([]);
    const [isEnd, setisEnd] = useState(false);
    const [isWaitingReply, setIsWaitingReply] = useState(false);
    
    // State management for preventing duplicate history processing
    const hasProcessedHistory = useRef(false);
    const setCurrentMessageFromHistoryCallback = useRef<((message: any) => void) | null>(null);
    
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

    // Monitor history message changes and automatically set last Agent message as CurrentMessage
    useEffect(() => {
        // Prevent duplicate processing
        if (hasProcessedHistory.current) {
            return;
        }
        
        // Boundary check: ensure userMessage is valid array
        if (!userMessage || !Array.isArray(userMessage) || userMessage.length === 0) {
            return;
        }

        // Boundary check: ensure callback is available
        if (!setCurrentMessageFromHistoryCallback.current) {
            console.warn('setCurrentMessageFromHistory callback not available');
            return;
        }

        try {
            // Check for the last Agent message
            const lastAgentMessage = checkLastAgentMessage(userMessage);
            
            if (lastAgentMessage) {
                // Additional validation before setting as current message
                if (!lastAgentMessage.id) {
                    console.warn('Found agent message without ID, skipping:', lastAgentMessage);
                    hasProcessedHistory.current = true;
                    return;
                }

                // Set as CurrentMessage (via callback)
                setCurrentMessageFromHistoryCallback.current(lastAgentMessage);
                
                // Remove this message from history with safety check
                if (setUserMessage) {
                    const updatedHistory = userMessage.filter(msg => msg !== lastAgentMessage);
                    setUserMessage(updatedHistory);
                } else {
                    console.warn('setUserMessage not available for history update');
                }
                
                // Mark as processed to prevent repeated execution
                hasProcessedHistory.current = true;
            }
        } catch (error) {
            console.error('Failed to process history message:', error, {
                userMessageLength: userMessage?.length,
                hasCallback: !!setCurrentMessageFromHistoryCallback.current
            });
            // Mark as processed even on error to avoid loop attempts
            hasProcessedHistory.current = true;
        }
    }, [userMessage, setUserMessage]);

    // Reset processing flag when chat room ID changes
    useEffect(() => {
        hasProcessedHistory.current = false;
    }, [id]);

    // Helper function to remove message from history (userMessage)
    const removeHistoryMessage = (messageToRemove: any) => {
        if (setUserMessage && userMessage) {
            const updatedHistory = userMessage.filter(msg => msg !== messageToRemove);
            setUserMessage(updatedHistory);
        }
    };

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
                        setInstruction={setInstruction}
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
                removeHistoryMessage={removeHistoryMessage}
                setCurrentMessageFromHistory={(callback) => {
                    setCurrentMessageFromHistoryCallback.current = callback;
                }}
                setInstruction={setInstruction}
            />
        </>
    );
}); 