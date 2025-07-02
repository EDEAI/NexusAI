/*
 * @LastEditors: biz
 */
import React, { FC } from 'react';
import { CopyButton } from '../ActionButtons/CopyButton';
import { SummaryButton } from '../ActionButtons/SummaryButton';

interface MessageActionsProps {
    messageApi?: any;
    index: number;
    idName: string;
    cidName: string;
    id?: any;
    agentChatRoomId?: any;
    isAgent: boolean;
}

export const MessageActions: FC<MessageActionsProps> = props => {
    const { messageApi, index, idName, cidName, id, agentChatRoomId, isAgent } = props;

    if (!isAgent) {
        return null;
    }

    return (
        <div className="flex gap-x-[20px]">
            <CopyButton
                messageApi={messageApi}
                index={index}
                idName={idName}
                cidName={cidName}
            />
            {!agentChatRoomId && (
                <SummaryButton
                    id={id}
                    index={index}
                    idName={idName}
                    cidName={cidName}
                />
            )}
        </div>
    );
}; 