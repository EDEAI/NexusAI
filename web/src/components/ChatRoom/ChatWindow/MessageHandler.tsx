/*
 * @LastEditors: biz
/*
 * @LastEditors: biz
 */
import useChatroomStore from '@/store/chatroomstate';
import { useIntl } from '@umijs/max';
import { ContentBlock } from '../types';
import {
    MCPToolRuntimeData,
    MCPToolStatus,
    WorkflowConfirmationStatus,
    MCPToolMessage,
    MCPToolMessageType,
} from '../types/mcp';
import { hasMessageContent } from '../utils';
import { parseMCPContent, reconstructContentWithUpdatedMCPTools } from '../utils/mcpParser';
import { useChatRoomContext } from '../context/ChatRoomContext';
import { useEffect, useRef } from 'react';

export const useMessageHandler = (
    setDisableInput: any,
    setIsStop: any,
    setSendValue: any,
    messageApi: any,
    setCurrentMessageContent: any,
    scrollDomRef: any,
    upButtonDom: any,
    agentList: any,
    setCurrentMessage: any,
    currentMessage: any,
    agentText: any,
    chatReturn: any,
    updateMCPTool?: (id: string | number, updates: Partial<MCPToolRuntimeData>) => void,
    getCurrentMessageList?: () => any[],
    setIsWaitingReply?: (waiting: boolean) => void,
    getMCPTool?: (id: string | number) => MCPToolRuntimeData | null,
    removeHistoryMessage?: (message: any) => void,
) => {
    const intl = useIntl();
    const setTruncatable = useChatroomStore(state => state.setTruncatable);
    const infoMessageTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});
    const latestGetMCPToolRef = useRef<typeof getMCPTool>(getMCPTool);

   

    const parseInstruction = (data: string): [string, any] | null => {
        try {
            const parsed = JSON.parse(data.slice(22, -2));
            return Array.isArray(parsed) && parsed.length >= 2 ? [parsed[0], parsed[1]] : null;
        } catch (error) {
            console.warn('Failed to parse instruction:', error);
            return null;
        }
    };

    const hasInstruction = (data: string): boolean => {
        return data.indexOf('--NEXUSAI-INSTRUCTION-') !== -1;
    };

    // Helper function to check if args contain need_upload values
    const checkNeedUploadInArgs = (args: any): boolean => {
        if (!args || !args.input_variables) return false;
        return Object.values(args.input_variables).some(value => value === 'need_upload');
    };

    // Helper function to manage contentBlocks for streaming messages
    const updateContentBlocks = (updateFn: (blocks: ContentBlock[]) => ContentBlock[]) => {
        setCurrentMessage((prev: any) => {
            const currentBlocks = prev.contentBlocks || [];
            const updatedBlocks = updateFn(currentBlocks);

            return {
                ...prev,
                contentBlocks: updatedBlocks,
            };
        });
    };

    // Helper function to append text to current text block or create new one
    const appendTextToCurrentBlock = (text: string) => {
        updateContentBlocks((blocks: ContentBlock[]) => {
            const lastBlock = blocks[blocks.length - 1];

            // If last block is text type, append to it
            if (lastBlock && lastBlock.type === 'text') {
                return blocks.map((block, index) =>
                    index === blocks.length - 1
                        ? { ...block, content: (block.content || '') + text }
                        : block,
                );
            } else {
                // Create new text block
                return [
                    ...blocks,
                    {
                        type: 'text',
                        content: text,
                        timestamp: Date.now(),
                    },
                ];
            }
        });
    };

    // Helper function to create MCP block
    const createMCPBlock = (toolId: string | number) => {
        updateContentBlocks((blocks: ContentBlock[]) => [
            ...blocks,
            {
                type: 'mcp',
                toolId,
                timestamp: Date.now(),
            },
        ]);
    };

    // Helper function to convert parsedContent.blocks to contentBlocks format
    const convertParsedContentToContentBlocks = (parsedContent: any): ContentBlock[] => {
        if (!parsedContent?.blocks || !Array.isArray(parsedContent.blocks)) {
            return [];
        }

        return parsedContent.blocks
            .map((block: any) => {
                if (block.type === 'text') {
                    return {
                        type: 'text',
                        content: block.content || '',
                        timestamp: Date.now(),
                    };
                } else if (block.type === 'mcp-tool' && block.toolData?.id) {
                    return {
                        type: 'mcp',
                        toolId: block.toolData.id,
                        timestamp: Date.now(),
                    };
                }
                // Skip invalid blocks
                return null;
            })
            .filter(Boolean) as ContentBlock[];
    };

    // Helper function to extract MCP tool IDs from contentBlocks
    const extractMCPToolIds = (contentBlocks: ContentBlock[]): (string | number)[] => {
        return contentBlocks
            .filter(block => block.type === 'mcp' && block.toolId)
            .map(block => block.toolId!);
    };

    // Helper function to update MCP tool state in current message and conversation
    const updateMCPToolState = (id: string | number, updates: Partial<MCPToolRuntimeData>) => {
        // 1. Prioritize updating conversation-level state (single source of truth)
        if (updateMCPTool) {
            updateMCPTool(id, updates);
        }

        // 2. Mark current message as containing this tool (for rendering identification)
        // Only update currentMessage if there's an active streaming session
        if (chatReturn.current && Object.keys(currentMessage).length > 0) {
            setCurrentMessage((prev: any) => {
                const currentActiveMCPTools = prev.activeMCPTools || [];
                const updatedActiveMCPTools = currentActiveMCPTools.includes(id)
                    ? currentActiveMCPTools
                    : [...currentActiveMCPTools, id];

                return {
                    ...prev,
                    activeMCPTools: updatedActiveMCPTools,
                };
            });
        }
    };

    // Helper function to sync conversation-level MCP tool states to contentBlocks
    const syncMCPToolStatesToContentBlocks = (
        contentBlocks: ContentBlock[],
        activeMCPTools: (string | number)[],
        getMCPTool: ((id: string | number) => MCPToolRuntimeData | null) | undefined,
    ): ContentBlock[] => {
        try {
            if (!contentBlocks || !Array.isArray(contentBlocks)) {
                console.warn(
                    'syncMCPToolStatesToContentBlocks: contentBlocks is not a valid array',
                );
                return [];
            }

            if (!getMCPTool) {
                console.warn('syncMCPToolStatesToContentBlocks: getMCPTool function not available');
                return contentBlocks;
            }

            // Ensure all activeMCPTools have corresponding contentBlocks
            const existingToolIds = contentBlocks
                .filter(block => block.type === 'mcp' && block.toolId)
                .map(block => block.toolId!);

            const missingToolIds = activeMCPTools.filter(id => !existingToolIds.includes(id));

            // Add missing MCP tools as new contentBlocks
            const additionalBlocks: ContentBlock[] = missingToolIds.map(toolId => ({
                type: 'mcp',
                toolId,
                timestamp: Date.now(),
            }));

            return [...contentBlocks, ...additionalBlocks];
        } catch (error) {
            console.error('Failed to sync MCP tool states to contentBlocks:', error);
            return contentBlocks;
        }
    };

    useEffect(() => {
        return () => {
            Object.values(infoMessageTimers.current).forEach(timer => clearTimeout(timer));
            infoMessageTimers.current = {};
        };
    }, []);

    useEffect(() => {
        latestGetMCPToolRef.current = getMCPTool;
    }, [getMCPTool]);

    const messageHandlers = {
        ERROR: (data: any) => {
            setDisableInput(false);
            setIsStop(false);
            setSendValue('');
            messageApi.open({
                type: 'error',
                content: `webSocket-${data}`,
                duration: 10,
            });
        },

        CHAT: (data: any) => {
            // First, check if there's an existing CurrentMessage that needs to be saved
            if (
                Object.keys(currentMessage).length &&
                hasMessageContent(currentMessage, {
                    checkText: true,
                    checkFiles: true,
                    checkMCPTools: true,
                    checkStreaming: true,
                    minTextLength: 1,
                })
            ) {
                // Save the current message to history before processing new user message
                const messageToSave = { ...currentMessage };

                // Enhanced MCP tool state synchronization (reuse ENDCHAT logic)
                if (
                    messageToSave.activeMCPTools?.length > 0 ||
                    messageToSave.contentBlocks?.length > 0
                ) {
                    // Sync conversation-level MCP tool states back to message
                    const updatedContentBlocks = syncMCPToolStatesToContentBlocks(
                        messageToSave.contentBlocks || [],
                        messageToSave.activeMCPTools || [],
                        getMCPTool,
                    );

                    // Reconstruct content with updated MCP tool states
                    if (getMCPTool && updatedContentBlocks.length > 0) {
                        const reconstructedContent = reconstructContentWithUpdatedMCPTools(
                            updatedContentBlocks,
                            getMCPTool,
                        );

                        if (reconstructedContent) {
                            messageToSave.content = reconstructedContent;
                            messageToSave.parsedContent = parseMCPContent(reconstructedContent);
                        } else {
                            // Fallback: use existing content parsing
                            if (messageToSave.content) {
                                messageToSave.parsedContent = parseMCPContent(
                                    messageToSave.content,
                                );
                            }
                        }
                    } else {
                        // Fallback: use existing content parsing
                        if (messageToSave.content) {
                            messageToSave.parsedContent = parseMCPContent(messageToSave.content);
                        }
                    }

                    // Preserve contentBlocks for rendering
                    messageToSave.contentBlocks = updatedContentBlocks;
                } else if (messageToSave.content) {
                    messageToSave.parsedContent = parseMCPContent(messageToSave.content);
                }

                // Add to current message content
                setCurrentMessageContent((pre: any) => pre.concat(messageToSave));

                // Clear the current message
                setCurrentMessage({});
            }

            // Process the new user message
            const userObj = {
                content: `${data}`,
                is_agent: 0,
            };
            setCurrentMessageContent((pre: any) => pre.concat(userObj));

            // Set waiting for reply state
            if (setIsWaitingReply) {
                setIsWaitingReply(true);
            }
            
            // Use requestAnimationFrame for better performance and avoiding potential memory leaks
            requestAnimationFrame(() => {
                if (scrollDomRef.current) {
                    scrollDomRef.current.scrollTop = 0;
                }
                if (upButtonDom.current) {
                    upButtonDom.current.style.display = 'none';
                }
            });
        },

        WITHFILELIST: (data: any) => {
            setCurrentMessageContent((pre: any) => {
                if (pre.length === 0) return pre;

                // Use immutable update pattern for better performance
                const lastIndex = pre.length - 1;
                return pre.map((item: any, index: number) =>
                    index === lastIndex ? { ...item, file_list: data } : item,
                );
            });
            // Use requestAnimationFrame for better performance and avoiding potential memory leaks
            requestAnimationFrame(() => {
                if (scrollDomRef.current) {
                    scrollDomRef.current.scrollTop = 0;
                }
                if (upButtonDom.current) {
                    upButtonDom.current.style.display = 'none';
                }
            });
        },

        STOPPABLE: (data: any) => {
            setIsStop(data);
        },

        TRUNCATABLE: (data: any) => {
            setTruncatable(data);
            if (!data) {
                messageApi.open({
                    type: 'success',
                    content: `${intl.formatMessage({
                        id: 'app.chatroom.sidebar.cleartips',
                    })}`,
                    duration: 3,
                });
            }
        },

        TRUNCATEOK: (data: any) => {
            messageApi.open({
                type: 'success',
                content: `${intl.formatMessage({ id: 'app.chatroom.sidebar.cleartips' })}`,
                duration: 3,
            });
        },

        MCPTOOLUSE: (data: any) => {
            const { id, name, skill_or_workflow_name, args, files_to_upload } = data;
            const isWorkflow =
                skill_or_workflow_name && skill_or_workflow_name.toLowerCase().includes('workflow');

            // Check if file upload is required
            const hasFilesToUpload = files_to_upload && Array.isArray(files_to_upload) && files_to_upload.length > 0;
            const needsFileUpload = hasFilesToUpload || checkNeedUploadInArgs(args);
            
            // Determine initial status
            const initialStatus = needsFileUpload ? MCPToolStatus.WAITING_FILE_UPLOAD : MCPToolStatus.RUNNING;

            // Update tool state
            updateMCPToolState(id, {
                name,
                skill_or_workflow_name: skill_or_workflow_name || name,
                args,
                status: initialStatus,
                isWorkflow,
                files_to_upload: files_to_upload || [],
                uploaded_files: []
            });
            // Clear waiting for reply state
            if (setIsWaitingReply) {
                setIsWaitingReply(false);
            }

            // Create MCP block in contentBlocks for ordered rendering
            createMCPBlock(id);
        },

        SHOWTOOLMSG: (data: any) => {
            if (!data) return;
            const { id, type, msg } = data;
            if (id === undefined || !type || !msg) {
                return;
            }

            const messageType = (type as MCPToolMessageType) || 'info';
            const messageKey = `runtime-${id}-${Date.now()}-${Math.random()}`;
            const newMessage: MCPToolMessage = {
                key: messageKey,
                type: messageType,
                text: msg,
                createdAt: Date.now(),
                transient: messageType === 'info',
                source: 'runtime',
            };

            const existingTool = getMCPTool ? getMCPTool(id) : null;
            const existingMessages = existingTool?.messages || [];
            const updatedMessages = [...existingMessages, newMessage];

            updateMCPToolState(id, {
                messages: updatedMessages,
                ...(messageType === 'warning' ? { msg } : {}),
            });

            if (messageType === 'info') {
                const timeoutId = setTimeout(() => {
                    const currentToolGetter = latestGetMCPToolRef.current;
                    const currentTool = currentToolGetter ? currentToolGetter(id) : null;
                    if (!currentTool?.messages) return;
                    const filteredMessages = currentTool.messages.filter(
                        messageEntry =>
                            messageEntry.key !== messageKey || messageEntry.type !== 'info',
                    );
                    if (filteredMessages.length === currentTool.messages.length) {
                        return;
                    }
                    updateMCPToolState(id, { messages: filteredMessages });
                    delete infoMessageTimers.current[messageKey];
                }, 3000);

                infoMessageTimers.current[messageKey] = timeoutId;
            }
        },

        WITHMCPTOOLRESULT: (data: any) => {
            const { id, result } = data;

            // Determine status based on result
            let status = MCPToolStatus.COMPLETED;
            if (typeof result === 'string') {
                try {
                    const parsedResult = JSON.parse(result);
                    if (parsedResult.status === 'failed') {
                        status = MCPToolStatus.FAILED;
                    }
                } catch {
                    // Keep as completed if not JSON
                }
            } else if (typeof result === 'object' && result?.status === 'failed') {
                status = MCPToolStatus.FAILED;
            }

            // Update tool with result
            updateMCPToolState(id, {
                result,
                status,
            });
        },

        WITHWFSTATUS: (data: any) => {
            const { id, status: confirmationData } = data;

            const workflowConfirmation: WorkflowConfirmationStatus = {
                id: confirmationData.id,
                status: confirmationData.status,
                app_run_id: confirmationData.app_run_id,
                node_exec_id: confirmationData.node_exec_id,
                workflow_name: confirmationData.workflow_name,
                need_user_confirm: confirmationData.need_user_confirm,
                show_todo_button: confirmationData.show_todo_button,
                confirmer_name: confirmationData.confirmer_name,
            };

            // Map workflow status to MCPToolStatus
            let mcpStatus: MCPToolStatus;
            switch (confirmationData.status) {
                case 'running':
                    mcpStatus = MCPToolStatus.RUNNING;
                    break;
                case 'waiting_confirm':
                    mcpStatus = MCPToolStatus.WAITING_CONFIRMATION;
                    break;
                case 'completed':
                    mcpStatus = MCPToolStatus.COMPLETED;
                    break;
                case 'failed':
                    mcpStatus = MCPToolStatus.FAILED;
                    break;
                default:
                    mcpStatus = MCPToolStatus.RUNNING; // Default to running for unknown statuses
                    break;
            }
            // Clear waiting for reply state
            if (setIsWaitingReply) {
                setIsWaitingReply(false);
            }

            // Update workflow with confirmation status
            updateMCPToolState(id, {
                workflow_confirmation: workflowConfirmation,
                status: mcpStatus,
                isWorkflow: true,
            });
        },

        WITHMCPTOOLFILES: (data: any) => {
            const { id, files_to_upload, args } = data;
            // Update tool data with uploaded files and input_variables
            updateMCPToolState(id, {
                uploaded_files: files_to_upload || [],
                status: MCPToolStatus.COMPLETED,
                ...(args ? { args } : {})
            });
        },
    };

    const addMessageHandler = (type: string, handler: (data: any) => void) => {
        messageHandlers[type] = handler;
    };

    const getSocketMessage = (message: any) => {
        let data = message.data;
        const array = parseInstruction(data);

        // Cache common string checks for better performance
        const hasInstructionMarker = hasInstruction(data);
        const hasReply = data.indexOf('REPLY') !== -1 && data.indexOf('ENDREPLY') === -1;
        const hasAbility = data.indexOf('ABILITY') !== -1;
        const hasEndChat = data.indexOf('ENDCHAT') !== -1;

        // Handle instruction-based messages first
        if (hasInstructionMarker) {
            if (!array) return;

            const messageType = array[0];
            const messageData = array[1];
            const handler = messageHandlers[messageType];

            if (handler) {
                handler(messageData);
            } else {
                console.warn(`Unknown message type: ${messageType}`);
            }
        }
        if (!hasInstructionMarker) {
            console.log(chatReturn.current, message);
        }
        // Handle streaming text content (only when NO instruction marker and chatReturn is active)
        if (!hasInstructionMarker && chatReturn.current) {
            // Update text accumulator immediately for responsiveness
            agentText.current += data;
            // Clear waiting for reply state
            if (setIsWaitingReply) {
                setIsWaitingReply(false);
            }

            // Batch DOM updates with requestAnimationFrame for better performance
            requestAnimationFrame(() => {
                if (scrollDomRef.current) {
                    scrollDomRef.current.scrollTop = 0;
                }
                if (upButtonDom.current) {
                    upButtonDom.current.style.display = 'none';
                }
            });

            // Update both content and contentBlocks for dual compatibility
            setCurrentMessage((pre: any) => {
                const updatedContent = agentText.current;
                const updatedMessage = {
                    ...pre,
                    content: updatedContent,
                };

                // Update parsedContent to reflect current content state
                if (updatedContent) {
                    updatedMessage.parsedContent = parseMCPContent(updatedContent);
                }

                return updatedMessage;
            });

            // Also append to contentBlocks for new rendering mode
            appendTextToCurrentBlock(data);
        }

        // Handle REPLY instruction (only when instruction marker is present)
        if (hasReply && hasInstructionMarker) {
            const agentId = array[1];

            
            let currentAgent = agentList.current.filter((item: any) => item.agent_id == agentId)[0];

            // Check if we need to merge with existing message or create new one
            setCurrentMessageContent((pre: any) => {
                // First, save the current message if it has meaningful content
                let updatedMessages = pre;
                if (
                    Object.keys(currentMessage).length &&
                    hasMessageContent(currentMessage, {
                        checkText: true,
                        checkFiles: true,
                        checkMCPTools: true,
                        checkStreaming: true,
                        minTextLength: 1,
                    })
                ) {
                    // --- begin: 同步 parsedContent、content ---
                    let messageToSave = { ...currentMessage };
                    if (
                        messageToSave.activeMCPTools?.length > 0 ||
                        messageToSave.contentBlocks?.length > 0
                    ) {
                        // Sync conversation-level MCP tool states back to message
                        const updatedContentBlocks = syncMCPToolStatesToContentBlocks(
                            messageToSave.contentBlocks || [],
                            messageToSave.activeMCPTools || [],
                            getMCPTool,
                        );

                        // Reconstruct content with updated MCP tool states
                        if (getMCPTool && updatedContentBlocks.length > 0) {
                            const reconstructedContent = reconstructContentWithUpdatedMCPTools(
                                updatedContentBlocks,
                                getMCPTool,
                            );

                            if (reconstructedContent) {
                                messageToSave.content = reconstructedContent;
                                messageToSave.parsedContent = parseMCPContent(reconstructedContent);
                            } else {
                                // Fallback: use existing content parsing
                                if (messageToSave.content) {
                                    messageToSave.parsedContent = parseMCPContent(
                                        messageToSave.content,
                                    );
                                }
                            }
                        } else {
                            // Fallback: use existing content parsing
                            if (messageToSave.content) {
                                messageToSave.parsedContent = parseMCPContent(messageToSave.content);
                            }
                        }

                        // Preserve contentBlocks for rendering
                        messageToSave.contentBlocks = updatedContentBlocks;
                    } else if (messageToSave.content) {
                        messageToSave.parsedContent = parseMCPContent(messageToSave.content);
                    }
                    // --- end: 同步 parsedContent、content ---
                    updatedMessages = pre.concat(messageToSave);
                }
                agentText.current = '';
                setCurrentMessage({
                    is_agent: 1,
                    icon: currentAgent?.icon,
                    name: currentAgent?.name,
                    avatar: currentAgent?.avatar,
                    content: '',
                    activeMCPTools: [],
                    agent_id: agentId,
                    // Initialize parsedContent for new message
                    parsedContent: null,
                    // Initialize empty contentBlocks for new streaming message
                    contentBlocks: [],
                });
                
                chatReturn.current = true;

                setIsStop(true);
                setTruncatable(false);
                return updatedMessages;
            });
        }

        // Handle ABILITY instruction (only when instruction marker is present)
        if (hasAbility && hasInstructionMarker) {
            let ability_id = array[1];

            setCurrentMessage((pre: any) => ({
                ...pre,
                is_agent: 1,
                ability_id: ability_id,
            }));
        }

        // Handle ENDCHAT
        if (hasEndChat) {
            chatReturn.current = false;
            agentText.current = '';
            setDisableInput(false);
            setIsStop(false);
            setTruncatable(true);
            if (Object.keys(currentMessage).length) {
                const messageToSave = { ...currentMessage };

                // Enhanced MCP tool state synchronization
                if (
                    messageToSave.activeMCPTools?.length > 0 ||
                    messageToSave.contentBlocks?.length > 0
                ) {
                    // Sync conversation-level MCP tool states back to message
                    const updatedContentBlocks = syncMCPToolStatesToContentBlocks(
                        messageToSave.contentBlocks || [],
                        messageToSave.activeMCPTools || [],
                        getMCPTool,
                    );

                    // Reconstruct content with updated MCP tool states
                    if (getMCPTool && updatedContentBlocks.length > 0) {
                        const reconstructedContent = reconstructContentWithUpdatedMCPTools(
                            updatedContentBlocks,
                            getMCPTool,
                        );

                        if (reconstructedContent) {
                            messageToSave.content = reconstructedContent;
                            messageToSave.parsedContent = parseMCPContent(reconstructedContent);
                        } else {
                            // Fallback: use existing content parsing
                            if (messageToSave.content) {
                                messageToSave.parsedContent = parseMCPContent(
                                    messageToSave.content,
                                );
                            }
                        }
                    } else {
                        // Fallback: use existing content parsing
                        if (messageToSave.content) {
                            messageToSave.parsedContent = parseMCPContent(messageToSave.content);
                        }
                    }

                    // Preserve contentBlocks for rendering
                    messageToSave.contentBlocks = updatedContentBlocks;
                } else if (messageToSave.content) {
                    messageToSave.parsedContent = parseMCPContent(messageToSave.content);
                }
                console.log(messageToSave);
                
                setCurrentMessageContent((pre: any) => pre.concat(messageToSave));
            }
            setCurrentMessage({});
            setSendValue('');
        }
    };

    return {
        getSocketMessage,
        addMessageHandler, // Expose method for adding new message types
    };
};
