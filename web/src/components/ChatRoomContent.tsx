/*
 * @LastEditors: biz
 */
import { message } from 'antd';
import 'highlight.js/styles/atom-one-dark.css';
import React, { FC, memo, useEffect } from 'react';
import { ChatContent } from './ChatRoom/ChatContent';
import { ChatRoomProvider, useChatRoomContext } from './ChatRoom/context/ChatRoomContext';
import { InputField } from './ChatRoom/InputField';

interface ChatRoomContentProps {
    agentList?: any;
    agentChatRoomId?: any;
    abilitiesList?: any;
    chatStatus?: any;
}

const ChatRoomContentInner: FC<ChatRoomContentProps> = memo(props => {
    const { agentList, agentChatRoomId, abilitiesList, chatStatus } = props;
    
    // Use context for chat room state management
    const {
        scrollDomRef,
        upButtonDom,
        isStop,
        setIsStop,
        instruction,
        setInstruction,
    } = useChatRoomContext();
    
    useEffect(() => {
        if (chatStatus == 1) {
            setIsStop(true);
        }
    }, [chatStatus]);

    const [messageApi, contextHolder] = message.useMessage();

    return (
        <>
            {contextHolder}
            <div
                className={`mx-[44px] flex justify-center relative box-border pt-[12px] h-full ${
                    agentChatRoomId ? 'w-full' : 'max-w-[1200px] !mx-auto px-[44px]'
                }`}
            >
                <div className="flex flex-col w-full h-full">
                    <ChatContent
                        instruction={instruction}
                        messageApi={messageApi}
                        scrollDomRef={scrollDomRef}
                        setIsStop={setIsStop}
                        upButtonDom={upButtonDom}
                        agentList={agentList}
                        agentChatRoomId={agentChatRoomId}
                        abilitiesList={abilitiesList}
                    />
                    <InputField
                        messageApi={messageApi}
                        isStop={isStop}
                        upButtonDom={upButtonDom}
                        scrollDomRef={scrollDomRef}
                        agentList={agentList}
                        agentChatRoomId={agentChatRoomId}
                        abilitiesList={abilitiesList}
                        chatStatus={chatStatus}
                    />
                </div>
            </div>
        </>
    );
});

export const ChatRoomContent: FC<ChatRoomContentProps> = memo(props => {
    

    return (
        <ChatRoomProvider agentChatRoomId={props.agentChatRoomId} agentList={props.agentList}>
            <ChatRoomContentInner {...props} />
        </ChatRoomProvider>
    );
});
