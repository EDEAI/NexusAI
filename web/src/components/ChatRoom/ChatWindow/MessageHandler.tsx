/*
 * @LastEditors: biz
/*
 * @LastEditors: biz
 */
import { useIntl } from '@umijs/max';
import useChatroomStore from '@/store/chatroomstate';
import { MCPToolRuntimeData, MCPToolStatus, WorkflowConfirmationStatus } from '../types/mcp';
import { parseMCPContent } from '../utils/mcpParser';

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
    getCurrentMessageList?: () => any[]
) => {
    const intl = useIntl();
    const setTruncatable = useChatroomStore(state => state.setTruncatable);

    const parseInstruction = (data: string): [string, any] | null => {
        try {
            const parsed = JSON.parse(data.slice(22, -2));
            return Array.isArray(parsed) && parsed.length >= 2 ? [parsed[0], parsed[1]] : null;
        } catch (error) {
            console.error('Failed to parse instruction:', error);
            return null;
        }
    };

    const hasInstruction = (data: string): boolean => {
        return data.indexOf('--NEXUSAI-INSTRUCTION-') !== -1;
    };

    // Helper function to update MCP tool state in current message and conversation
    const updateMCPToolState = (id: string | number, updates: Partial<MCPToolRuntimeData>) => {
        // Update conversation state if function is provided
        if (updateMCPTool) {
            updateMCPTool(id, updates);
            
        }
        
        return
        // Also update current message state for consistency
        setCurrentMessage((prev: any) => {
            // Initialize mcpTools array if it doesn't exist
            const currentTools = prev.mcpTools || [];
            
            // Find existing tool by id or create new one
            const existingToolIndex = currentTools.findIndex((tool: MCPToolRuntimeData) => tool.id === id);
            
            let updatedTools;
            if (existingToolIndex >= 0) {
                // Update existing tool using immutable pattern
                updatedTools = currentTools.map((tool: MCPToolRuntimeData, index: number) =>
                    index === existingToolIndex 
                        ? { ...tool, ...updates }
                        : tool
                );
            } else {
                // Add new tool using concat for better performance
                const newTool = {
                    id,
                    status: MCPToolStatus.PENDING,
                    name: '',
                    skill_or_workflow_name: '',
                    workflow_run_id: 0,
                    workflow_confirmation_status: null,
                    args: {},
                    result: null,
                    ...updates
                };
                updatedTools = currentTools.concat(newTool);
            }
            debugger
            return {
                ...prev,
                mcpTools: updatedTools
            };
        });
    };

  
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
            const userObj = {
                content: `${data}`,
                is_agent: 0,
            };
            setCurrentMessageContent((pre: any) => 
                pre.concat(userObj)
            );
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
                    index === lastIndex 
                        ? { ...item, file_list: data }
                        : item
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
            console.log('MCPTOOLUSE data:', data);
            
            const { id, name, skill_or_workflow_name, args } = data;
            const isWorkflow = skill_or_workflow_name && skill_or_workflow_name.toLowerCase().includes('workflow');
            
            // Start tool in running state
            updateMCPToolState(id, {
                name,
                skill_or_workflow_name: skill_or_workflow_name || name,
                args,
                status: MCPToolStatus.RUNNING,
                isWorkflow
            });
        },

        WITHMCPTOOLRESULT: (data: any) => {
            console.log('WITHMCPTOOLRESULT data:', data);
            
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
                status
            });
        },

        WITHWFSTATUS: (data: any) => {
            console.log('WITHWFSTATUS data:', data);
            
            const { id, status: confirmationData } = data;
            
            const workflowConfirmation: WorkflowConfirmationStatus = {
                id: confirmationData.id,
                status: confirmationData.status,
                app_run_id: confirmationData.app_run_id,
                node_exec_id: confirmationData.node_exec_id,
                workflow_name: confirmationData.workflow_name,
                need_user_confirm: confirmationData.need_user_confirm,
                show_todo_button: confirmationData.show_todo_button,
                confirmer_name: confirmationData.confirmer_name
            };
            
            // Update workflow with confirmation status
            updateMCPToolState(id, {
                workflow_confirmation: workflowConfirmation,
                status: MCPToolStatus.WAITING_CONFIRMATION,
                isWorkflow: true
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
        const hasReply = data.indexOf('REPLY') !== -1;
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
        
        // Handle REPLY instruction (only when instruction marker is present)
        if (hasReply && hasInstructionMarker) {
            let agentId = array[1];
            
            let currentAgent = agentList.current.filter(
                (item: any) => item.agent_id == agentId,
            )[0];
            
            // Check if we need to merge with existing message or create new one
            setCurrentMessageContent((pre: any) => {
                // First, save the current message if it has meaningful content
                let updatedMessages = pre;
                if (Object.keys(currentMessage).length && (currentMessage.content || currentMessage.mcpTools?.length)) {
                    updatedMessages = pre.concat(currentMessage);
                }
                
                // Get the complete message list including history and current messages
                let completeMessageList = [];
                if (getCurrentMessageList) {
                    const historyMessages = getCurrentMessageList();
                    completeMessageList = [...historyMessages, ...updatedMessages];
                } else {
                    completeMessageList = updatedMessages;
                }
                
                // Check if the last message in the complete list is from the same agent
                const lastMessage = completeMessageList[completeMessageList.length - 1];
                const shouldMergeWithLastMessage = lastMessage && 
                    lastMessage.is_agent === 1 && 
                    lastMessage.agent_id == agentId;
                    debugger
                if (shouldMergeWithLastMessage) {
                    // Check if the last message is in current messages or history
                    const isLastMessageInCurrent = updatedMessages.length > 0 && 
                        updatedMessages[updatedMessages.length - 1] === lastMessage;
                    
                    if (isLastMessageInCurrent) {
                        // Merge with existing message in current list: continue using the last message
                        // Extract pure text content from parsedContent if available
                        let pureTextContent = '';
                        if (lastMessage.parsedContent && lastMessage.parsedContent.blocks) {
                            pureTextContent = lastMessage.parsedContent.blocks
                                .filter(block => block.type === 'text')
                                .map(block => block.content)
                                .join('');
                        } else {
                            // Fallback to original content if parsedContent is not available
                            pureTextContent = lastMessage.content || '';
                        }
                        
                        agentText.current = pureTextContent;
                        setCurrentMessage({
                            ...lastMessage,
                            // Keep existing properties but ensure agent_id is set
                            agent_id: agentId,
                            // Set content to pure text only
                            content: pureTextContent,
                            // Preserve parsedContent if it exists
                            parsedContent: lastMessage.parsedContent
                        });
                        
                        // Remove the last message from the list since we're continuing it
                        chatReturn.current = true;
                        setIsStop(true);
                        setTruncatable(false);
                        return updatedMessages.slice(0, -1);
                    } else {
                        // Last message is in history, continue from where it left off
                        // Extract pure text content from parsedContent if available
                        let pureTextContent = '';
                        if (lastMessage.parsedContent && lastMessage.parsedContent.blocks) {
                            pureTextContent = lastMessage.parsedContent.blocks
                                .filter(block => block.type === 'text')
                                .map(block => block.content)
                                .join('');
                        } else {
                            // Fallback to original content if parsedContent is not available
                            pureTextContent = lastMessage.content || '';
                        }
                        
                        agentText.current = pureTextContent;
                        setCurrentMessage({
                            ...lastMessage,
                            agent_id: agentId,
                            // Set content to pure text only for continuation
                            content: pureTextContent,
                            // Preserve parsedContent if it exists, will be updated as content changes
                            parsedContent: lastMessage.parsedContent
                        });
                        
                        chatReturn.current = true;
                        setIsStop(true);
                        setTruncatable(false);
                        return updatedMessages;
                    }
                } else {
                    // Create a new agent message
                    agentText.current = '';
                    setCurrentMessage({
                        is_agent: 1,
                        icon: currentAgent?.icon,
                        name: currentAgent?.name,
                        content: '',
                        mcpTools: [],
                        agent_id: agentId,
                        // Initialize parsedContent for new message
                        parsedContent: null
                    });
                    
                    chatReturn.current = true;
                    setIsStop(true);
                    setTruncatable(false);
                    return updatedMessages;
                }
                
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
        
        // Handle streaming text content (only when NO instruction marker and chatReturn is active)
        if (!hasInstructionMarker && chatReturn.current) {
            // Update text accumulator immediately for responsiveness
            agentText.current += data;
            
            // Batch DOM updates with requestAnimationFrame for better performance
            requestAnimationFrame(() => {
                if (scrollDomRef.current) {
                    scrollDomRef.current.scrollTop = 0;
                }
                if (upButtonDom.current) {
                    upButtonDom.current.style.display = 'none';
                }
            });
            
            // Update message content state and parsedContent in real-time
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
        }
        
        // Handle ENDCHAT
        if (hasEndChat) {
            chatReturn.current = false;
            agentText.current = '';
            setDisableInput(false);
            setIsStop(false);
            setTruncatable(true);
            if (Object.keys(currentMessage).length) {
                // Add parsedContent to the completed message for consistent rendering
                const messageToSave = { ...currentMessage };
                if (messageToSave.content) {
                    messageToSave.parsedContent = parseMCPContent(messageToSave.content);
                }
                
                setCurrentMessageContent((pre: any) => 
                    pre.concat(messageToSave)
                );
            }
            setCurrentMessage({});
            setSendValue('');
        }
    };

    return { 
        getSocketMessage,
        addMessageHandler  // Expose method for adding new message types
    };
}; 