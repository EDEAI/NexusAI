/*
 * @LastEditors: biz
 */
import React, { FC } from 'react';
import Avatar from '@/components/ChatAvatar';
import { userinfodata } from '@/utils/useUser';
import { MessageContent } from '../MessageDisplay/MessageContent';
import { parseMCPContent } from '../utils/mcpParser';
import { MCPToolRuntimeData } from '../types/mcp';

interface CurrentMessageProps {
    currentMessage: any;
    agentChatRoomId?: any;
    intl: any;
    mcpTools?: Record<string | number, MCPToolRuntimeData>;
    updateMCPTool?: (id: string | number, updates: Partial<MCPToolRuntimeData>) => void;
    getMCPTool?: (id: string | number) => MCPToolRuntimeData | null;
}

export const CurrentMessage: FC<CurrentMessageProps> = props => {
    const { 
        currentMessage, 
        agentChatRoomId, 
        intl, 
        mcpTools = {}, 
        updateMCPTool = () => {}, 
        getMCPTool = () => null 
    } = props;

    if (!currentMessage.name) {
        return null;
    }

    return (
        <div
            className={`w-full flex gap-[15px] pt-[15px] pb-[15px] ${
                currentMessage.is_agent != 1 ? 'flex-row-reverse' : ''
            }`}
        >
            {currentMessage.is_agent == 1 ? (
                <Avatar data={currentMessage} />
            ) : (
                <Avatar data={{ avatar: '/icons/user_header.svg' }} />
            )}
            <div
                className={`flex1 ${agentChatRoomId ? '' : 'max-w-[560px]'} text-right`}
                id={`addcontent`}
            >
                <div
                    className={`${
                        currentMessage.is_agent == 1 ? 'text-left' : 'text-right'
                    } font-[500] text-[14px] text-[#213044] pb-[8px]`}
                >
                    {currentMessage.name
                        ? currentMessage.name
                        : userinfodata('GET').nickname}
                </div>
                <div
                    className={`flex ${
                        currentMessage.is_agent == 1 ? 'flex-row' : 'flex-row-reverse'
                    }`}
                >
                    <MessageContent
                        content={currentMessage.content || ''}
                        fileList={currentMessage.file_list}
                        index={-1}
                        intl={intl}
                        isAgent={currentMessage.is_agent == 1}
                        contentId="addchilContent"
                        mcpTools={mcpTools}
                        updateMCPTool={updateMCPTool}
                        getMCPTool={getMCPTool}
                        item={{
                            ...currentMessage,
                            parsedContent: parseMCPContent(currentMessage.content || '')
                        }}
                        isCurrentMessage={true}
                        contentBlocks={currentMessage.contentBlocks}
                    />
                </div>
            </div>
        </div>
    );
}; 