import { getRoomMessage } from '@/api/plaza';
import useChatroomStore from '@/store/chatroomstate';
import { useIntl } from '@umijs/max';
import { Spin } from 'antd';
import React, { FC, memo, useEffect, useRef, useState } from 'react';
import { useLocation, useParams } from 'umi';
import { MeetingSummaryButton } from '../ActionButtons/MeetingSummaryButton';
import { MessageItem } from '../MessageDisplay/MessageItem';
import { CurrentConversation } from './CurrentConversation';
import { MCPToolRuntimeData, MCPToolStatus, getMCPToolStatus } from '../types/mcp';
import { parseMCPContent } from '../utils/mcpParser';

interface ChatContentProps {
    instruction?: any;
    setInstruction?: any;
    messageApi?: any;
    scrollDomRef?: any;
    setIsStop?: any;
    upButtonDom?: any;
    agentList?: any;
    agentChatRoomId?: any;
    abilitiesList?: any;
}

export const ChatContent: FC<ChatContentProps> = memo(props => {
    const {
        messageApi,
        scrollDomRef,
        instruction,
        setIsStop,
        upButtonDom,
        setInstruction,
        agentList,
        agentChatRoomId,
        abilitiesList,
    } = props;

    const intl = useIntl();
    const [bminWidth, setbminWidth] = useState(860);

    // Get both URL params and search params
    const { id: urlParamId } = useParams<{ id: string }>();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const searchParamId = searchParams.get('id');

    // Use URL param id if available, otherwise use search param id
    const id = agentChatRoomId || urlParamId || searchParamId;

    // chat history
    const [userMessage, setUserMessage] = useState([]);
    // Whether to show the down arrow button
    const isupButtonShow = useRef(false);
    // WebSocket trigger command
    const [sendValue, setSendValue] = useState('');
    // Loading
    const scrollDomload = useRef(null);
    // Whether to load on upward scroll
    const isUpload = useRef(true);

    // MCP tool state management for current conversation
    const [mcpTools, setMcpTools] = useState<Record<string | number, MCPToolRuntimeData>>({});

    const roomMessageContentpage = useRef(2);
    const roomMessagepage = useRef(1);
    const newAddLength = useRef(0);

    // Update MCP tool state
    const updateMCPTool = (id: string | number, updates: Partial<MCPToolRuntimeData>) => {
        setMcpTools(prev => {
            const existingTool = prev[id];
            
            if (existingTool) {
                // Update existing tool
                return {
                    ...prev,
                    [id]: {
                        ...existingTool,
                        ...updates
                    }
                };
            } else {
                // Create new tool with default values
                return {
                    ...prev,
                    [id]: {
                        id,
                        status: MCPToolStatus.PENDING,
                        name: '',
                        skill_or_workflow_name: '',
                        workflow_run_id: 0,
                        workflow_confirmation_status: null,
                        args: {},
                        result: null,
                        ...updates
                    }
                };
            }
        });
    };

    // Get MCP tool state
    const getMCPTool = (id: string | number): MCPToolRuntimeData | null => {
        return mcpTools[id] || null;
    };

    // Process historical messages to extract and register MCP tools
    const processHistoricalMessages = (messages: any[]): any[] => {
        const processedMessages = messages.map(message => {
            // Create a copy to avoid mutating original data
            const processedMessage = { ...message };
            
            if (message.is_agent === 1 && message.content) {
                const parsedContent = parseMCPContent(message.content);
                
                // Save parsed content to message object for consistent rendering
                processedMessage.parsedContent = parsedContent;
                
                if (parsedContent.hasMCPTools) {
                    parsedContent.blocks.forEach(block => {
                        if (block.type === 'mcp-tool' && block.toolData) {
                            const toolData = block.toolData;
                            
                            // Register MCP tool in conversation state if not already exists
                            if (!mcpTools[toolData.id]) {
                                const status = getMCPToolStatus(
                                    toolData.workflow_confirmation_status, 
                                    toolData.result
                                );
                                
                                setMcpTools(prev => ({
                                    ...prev,
                                    [toolData.id]: {
                                        id: toolData.id,
                                        name: toolData.name,
                                        skill_or_workflow_name: toolData.skill_or_workflow_name || toolData.name,
                                        workflow_run_id: toolData.workflow_run_id || 0,
                                        workflow_confirmation_status: toolData.workflow_confirmation_status || null,
                                        args: toolData.args || {},
                                        result: toolData.result || null,
                                        status,
                                        isWorkflow: toolData.skill_or_workflow_name ? 
                                            toolData.skill_or_workflow_name.toLowerCase().includes('workflow') : false
                                    }
                                }));
                            }
                        }
                    });
                }
            }
            
            return processedMessage;
        });
        
        return processedMessages;
    };

    // Retrieve chat history
    const getChatHistory = async (init: boolean, toTOP: any = () => {}) => {
        if (id) {
            let res = await getRoomMessage(id, {
                page: roomMessagepage.current,
                page_size: 10,
            });
            if (res.code == 0) {
                roomMessageContentpage.current = res.data.total_pages;
                if (!init) {
                    scrollDomload.current.style.display = 'none';
                }
               
                setUserMessage(pre => {
                    const newMessages = res.data.list.reverse();
                    const processedMessages = processHistoricalMessages(newMessages);
                    
                    return init
                        ? [...processedMessages]
                        : [...pre, ...processedMessages];
                });
                if (init) {
                    if (scrollDomRef && scrollDomRef.current) {
                        setTimeout(() => {
                            scrollDomRef.current.scrollTop = 0;
                            upButtonDom.current.style.display = 'none';
                        });
                    }
                } else {
                    newAddLength.current = res.data.list.length;
                }
                isUpload.current = true;
            }
        }
    };

    // Scroll movement
    const slideScroll = (e: any) => {
        let scrollPosition = e.target.scrollHeight + (e.target.scrollTop - e.target.clientHeight);
        if (isupButtonShow.current !== Math.ceil(e.target.scrollTop) < -50) {
            isupButtonShow.current = Math.ceil(e.target.scrollTop) < -50;
            upButtonDom.current.style.display = isupButtonShow.current ? 'flex' : 'none';
        }
        if (scrollPosition < 10 && isUpload.current) {
            isUpload.current = false;
            roomMessagepage.current = roomMessagepage.current + 1;
            scrollDomload.current.style.display = 'flex';
            if (roomMessageContentpage.current >= roomMessagepage.current) {
                getChatHistory(false);
            } else {
                scrollDomload.current.style.display = 'none';
            }
        }
    };

    // WebSocket send command
    const setsendMessageinit = (type: string, value: any) => {
        if (value === '0') value = Number(value);
        // Handle 0 as a valid value, only convert empty string, null, undefined to null
        let initChatRoomstok = [
            `${type}`,
            value !== '' && value !== null && value !== undefined ? value : null,
        ];
        setSendValue(JSON.stringify(initChatRoomstok));
    };

    const disableInput = useChatroomStore(state => state.disableInput);
    const clearMemory = useChatroomStore(state => state.clearMemory);

    useEffect(() => {
        clearMemory && clearMemory.length && setsendMessageinit(clearMemory[0], clearMemory[1]);
    }, [clearMemory]);

    useEffect(() => {
        if (instruction && instruction.length) {
            setsendMessageinit(instruction[0], instruction[1] !== undefined ? instruction[1] : '');
            setInstruction([]);
        }
    }, [instruction]);

    useEffect(() => {
        roomMessagepage.current = 1;
        getChatHistory(true);
    }, []);

    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth < 1280) {
            } else {
                setbminWidth(window.innerWidth - 320 - (window.innerWidth - 320) / 2 - 88);
            }
        };

        handleResize();
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    return (
        <div className="flex-1 min-h-0">
            <div
                className={`h-full min-h-full overflow-y-auto flex flex-col-reverse items-center scroll-smooth chatroom`}
                ref={scrollDomRef}
                onScroll={slideScroll}
            >
                <div
                    className="w-full"
                    style={{ minWidth: agentChatRoomId ? '' : `${bminWidth}px` }}
                >
                    <div className="w-full">
                        <div className="flex flex-col-reverse">
                            {userMessage && userMessage.length ? (
                                userMessage.map((item, index) => (
                                    <MessageItem
                                        key={index}
                                        item={{ ...item, id: `c${item.id}` }}
                                        index={index}
                                        agentChatRoomId={agentChatRoomId}
                                        abilitiesList={abilitiesList}
                                        messageApi={messageApi}
                                        id={id}
                                        idName="content"
                                        cidName="chilContent"
                                        mcpTools={mcpTools}
                                        updateMCPTool={updateMCPTool}
                                        getMCPTool={getMCPTool}
                                    />
                                ))
                            ) : (
                                <></>
                            )}
                        </div>
                        <CurrentConversation
                            messageApi={messageApi}
                            setUserMessage={setUserMessage}
                            sendValue={sendValue}
                            agentList={agentList}
                            scrollDomRef={scrollDomRef}
                            upButtonDom={upButtonDom}
                            setIsStop={setIsStop}
                            setSendValue={setSendValue}
                            agentChatRoomId={agentChatRoomId}
                            abilitiesList={abilitiesList}
                            mcpTools={mcpTools}
                            updateMCPTool={updateMCPTool}
                            getMCPTool={getMCPTool}
                            userMessage={userMessage}
                        />
                    </div>
                    <div className="w-full flex justify-center pb-[10px]">
                        {!agentChatRoomId && !disableInput && userMessage.length ? (
                            <MeetingSummaryButton roomid={id} />
                        ) : (
                            <></>
                        )}
                    </div>
                </div>
                <div
                    className="text-center justify-center items-center flex"
                    style={{ display: 'none' }}
                    ref={scrollDomload}
                >
                    <Spin />
                </div>
            </div>
        </div>
    );
}); 