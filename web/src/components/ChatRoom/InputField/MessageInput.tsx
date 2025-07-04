/*
 * @LastEditors: biz
 */
import React, { FC } from 'react';
import { PauseCircleOutlined, UploadOutlined } from '@ant-design/icons';
import { Button, Input } from 'antd';
import { useIntl } from '@umijs/max';
import { throttle } from 'lodash';

const { TextArea } = Input;

interface MessageInputProps {
    userSendvalue: string;
    setUserSendvalue: (value: string) => void;
    disableInput: boolean;
    isUploading: boolean;
    isStop: boolean;
    userSendmessage: (e: any) => void;
    handleFileUpload: () => void;
    sendMessage: (message: string) => void;
    stopChatRoom: () => void;
}

export const MessageInput: FC<MessageInputProps> = props => {
    const {
        userSendvalue,
        setUserSendvalue,
        disableInput,
        isUploading,
        isStop,
        userSendmessage,
        handleFileUpload,
        sendMessage,
        stopChatRoom,
    } = props;
    const intl = useIntl();

    const handleSendClick = throttle(() => {
        if (disableInput || !userSendvalue) return false;
        sendMessage(userSendvalue);
    }, 300);

    return (
        <div className={`flex items-center gap-[10px] box-border`}>
            <Button
                type="text"
                icon={<UploadOutlined />}
                onClick={handleFileUpload}
                disabled={disableInput || isUploading}
                loading={isUploading}
            />

            <TextArea
                id="userValue"
                className="placeholder-text-[#aaa] placeholder-text-[14px]"
                autoSize={{ minRows: 1, maxRows: 6 }}
                value={userSendvalue}
                disabled={disableInput}
                onChange={(e: any) => {
                    setUserSendvalue(e.target.value);
                }}
                onPressEnter={userSendmessage}
                style={{
                    height: '34px',
                    border: 'none',
                    resize: 'none',
                    backgroundColor: 'transparent',
                }}
                placeholder={`${intl.formatMessage({
                    id: 'app.chatroom.content.input',
                })}…`}
            />
            {!isStop ? (
                <div
                    className={`${
                        disableInput || !userSendvalue ? 'bg-[#ddd]' : 'bg-[#1B64F3]'
                    } min-w-[30px] h-[30px]  flex items-center justify-center cursor-pointer rounded-[6px]`}
                    onClick={handleSendClick}
                >
                    <img
                        src="/icons/send_icon_w.svg"
                        alt=""
                        className="w-[18px] h-[18px]"
                    />
                </div>
            ) : (
                <div
                    className="min-w-[34px] h-[34px] bg-[#000] flex items-center justify-center cursor-pointer rounded-[4px]"
                    onClick={stopChatRoom}
                >
                    <PauseCircleOutlined style={{ color: '#fff', fontSize: '20px' }} />
                </div>
            )}
        </div>
    );
}; 