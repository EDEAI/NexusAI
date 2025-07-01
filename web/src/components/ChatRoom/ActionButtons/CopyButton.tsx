/*
 * @LastEditors: biz
 */
import React, { FC, memo, useState } from 'react';
import { useIntl } from '@umijs/max';
import { copyToClipboard } from '../utils/clipboard';

interface CopyButtonProps {
    messageApi?: any;
    index?: number;
    idName: string;
    cidName: string;
}

export const CopyButton: FC<CopyButtonProps> = memo(props => {
    const { messageApi, index, idName, cidName } = props;
    const intl = useIntl();
    const [iconHover, setIconHover] = useState(false);

    return (
        <div className="flex gap-x-[4px]">
            <div
                onMouseEnter={() => {
                    setIconHover(true);
                }}
                onMouseLeave={() => {
                    setIconHover(false);
                }}
                className=" p-[2px] cursor-pointer rounded-md flex gap-x-[5px] items-center pt-[10px]"
                onClick={async (e: any) => {
                    const dom = e.target.closest(`#${idName}${index}`);
                    const childElement = dom.querySelector(`#${cidName}${index}`);
                    try {
                        const success = await copyToClipboard(childElement.innerText);
                        if (success) {
                            messageApi.open({
                                type: 'success',
                                content: intl.formatMessage({ id: 'app.chatroom.content.copySucceed' }),
                                duration: 2,
                            });
                        } else {
                            messageApi.open({
                                type: 'error',
                                content: intl.formatMessage({ id: 'app.chatroom.content.copyFailed' }) || 'Copy failed',
                                duration: 2,
                            });
                        }
                    } catch (err) {
                        console.error('Failed to copy text: ', err);
                        messageApi.open({
                            type: 'error',
                            content: intl.formatMessage({ id: 'app.chatroom.content.copyFailed' }) || 'Copy failed',
                            duration: 2,
                        });
                    }
                }}
            >
                <img
                    src={`${!iconHover ? '/icons/chat_copy.svg' : '/icons/chat_copy_check.svg'}`}
                    className="w-[16px] h-[16px]"
                    alt="copy"
                />
                <span className={`text-[12px] ${!iconHover ? 'text-[#666]' : ' text-[#1B64F3]'}`}>
                    {intl.formatMessage({ id: 'app.chatroom.content.copy' })}
                </span>
            </div>
        </div>
    );
}); 