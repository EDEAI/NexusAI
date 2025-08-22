/*
 * @LastEditors: biz
 */
import React, { FC, useEffect } from 'react';
import { useIntl } from '@umijs/max';
import Avatar from '@/components/ChatAvatar';
import { useUserInfo } from '@/hooks/useUserInfo';
import { MessageContent } from './MessageContent';
import { MessageActions } from './MessageActions';
import { MCPToolRuntimeData } from '../types/mcp';
import { hasMessageContent } from '../utils';
import { useChatRoomContext } from '../context/ChatRoomContext';

interface MessageItemProps {
    item: any;
    index: number;
    agentChatRoomId?: any;
    abilitiesList?: any[];
    messageApi?: any;
    id?: any;
    idName: string;
    cidName: string;
    mcpTools?: Record<string | number, MCPToolRuntimeData>;
    updateMCPTool?: (id: string | number, updates: Partial<MCPToolRuntimeData>) => void;
    getMCPTool?: (id: string | number) => MCPToolRuntimeData | null;
}

export const MessageItem: FC<MessageItemProps> = props => {
    const { 
        item, 
        index, 
        agentChatRoomId, 
        abilitiesList, 
        messageApi, 
        id, 
        idName, 
        cidName,
        mcpTools,
        updateMCPTool,
        getMCPTool
    } = props;
    const intl = useIntl();
    const isAgent = item.is_agent === 1;
    const { userInfo } = useUserInfo();

    // New: Smart content check - hide empty historical messages
    if (!hasMessageContent(item)) {
        return null;
    }

    return (
        <div
            className={`w-full flex gap-[15px] pt-[15px] pb-[15px] ${
                !isAgent ? 'flex-row-reverse' : ''
            }`}
        >
            {isAgent ? (
                <Avatar data={item} />
            ) : (
                <Avatar data={{ avatar: '/icons/user_header.svg' }} />
            )}
            <div
                className={`flex1 ${agentChatRoomId ? '' : 'max-w-[560px]'} text-right`}
                id={`${idName}${index}`}
            >
                <div
                    className={`${
                        isAgent ? 'text-left' : 'text-right'
                    } font-[500] text-[14px] text-[#213044] pb-[8px]`}
                >
                    {item.name ? item.name : userInfo?.nickname || ''}
                    {item.ability_id > 0 && (
                        <>
                            {' '}
                            (
                            {abilitiesList?.find(x => item.ability_id == x.value)?.label ||
                                intl.formatMessage({
                                    id: 'app.chatroom.content.abilityNotFound',
                                })}
                            )
                        </>
                    )}
                </div>
                <div
                    className={`flex ${
                        isAgent ? 'flex-row' : 'flex-row-reverse'
                    }`}
                >
                   
                    <MessageContent
                        content={item.content}
                        fileList={item.file_list}
                        index={index}
                        intl={intl}
                        isAgent={isAgent}
                        contentId={`${cidName}${index}`}
                        mcpTools={mcpTools}
                        updateMCPTool={updateMCPTool}
                        getMCPTool={getMCPTool}
                        item={item}
                    />
                </div>
                <MessageActions
                    messageApi={messageApi}
                    index={index}
                    idName={idName}
                    cidName={cidName}
                    id={id}
                    agentChatRoomId={agentChatRoomId}
                    isAgent={isAgent}
                />
            </div>
        </div>
    );
};