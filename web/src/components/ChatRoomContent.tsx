/*
 * @LastEditors: biz
 */
import { message } from 'antd';
import 'highlight.js/styles/atom-one-dark.css';
import React, { FC, memo, useEffect } from 'react';
import { ChatContent } from './ChatRoom/ChatContent';
import { useChatRoom } from './ChatRoom/hooks/useChatRoom';
import { InputField } from './ChatRoom/InputField';

interface ChatRoomContentProps {
    agentList?: any;
    agentChatRoomId?: any;
    abilitiesList?: any;
    chatStatus?: any;
}
export const ChatRoomContent: FC<ChatRoomContentProps> = memo(props => {
    const { agentList, agentChatRoomId, abilitiesList, chatStatus } = props;
    
    // Use custom hook for chat room state management
    const {
        scrollDomRef,
        upButtonDom,
        isStop,
        setIsStop,
        instruction,
        setInstruction,
    } = useChatRoom(agentChatRoomId);
    useEffect(() => {
        console.log(chatStatus);
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
                        setInstruction={setInstruction}
                        messageApi={messageApi}
                        scrollDomRef={scrollDomRef}
                        setIsStop={setIsStop}
                        upButtonDom={upButtonDom}
                        agentList={agentList}
                        agentChatRoomId={agentChatRoomId}
                        abilitiesList={abilitiesList}
                    />
                    <InputField
                        setInstruction={setInstruction}
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
