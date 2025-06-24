/*
 * @LastEditors: biz
 */
import React, { FC, useEffect, useState } from 'react';
import { FileDoneOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import useChatroomStore from '@/store/chatroomstate';

interface SummaryButtonProps {
    id: any;
    index?: number;
    idName: string;
    cidName: string;
}

export const SummaryButton: FC<SummaryButtonProps> = props => {
    const { id, index, idName, cidName } = props;
    const intl = useIntl();
    const setSummaryClick = useChatroomStore(state => state.setSummaryClick);
    const [disabled, setDisabled] = useState(true);
    const summaryClick = useChatroomStore(state => state.summaryClick);
    
    useEffect(() => {
        setDisabled(summaryClick);
    }, [summaryClick]);
    
    const setSummaryParams = useChatroomStore(state => state.setSummaryParams);
    
    return (
        <div
            className={`flex gap-x-[4px] text-[#666] ${
                disabled ? 'cursor-pointer hover:text-[#1B64F3]' : 'cursor-no-drop'
            }`}
        >
            <div
                className=" p-[2px]  rounded-md flex gap-x-[5px] items-center pt-[10px]"
                onClick={(e: any) => {
                    if (disabled) {
                        const dom = e.target.closest(`#${idName}${index}`);
                        const childElement = dom.querySelector(`#${cidName}${index}`);
                        setSummaryParams({ id: id, message: childElement.innerText });
                        setSummaryClick(false);
                    }
                }}
            >
                <FileDoneOutlined className="text-[16px]" />
                <span className="text-[12px]">
                    {intl.formatMessage({ id: 'app.chatroom.content.summary' })}
                </span>
            </div>
        </div>
    );
}; 