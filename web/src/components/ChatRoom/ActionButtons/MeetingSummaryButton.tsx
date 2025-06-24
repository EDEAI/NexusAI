/*
 * @LastEditors: biz
 */
import React, { FC, useEffect, useState } from 'react';
import { FundProjectionScreenOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import useChatroomStore from '@/store/chatroomstate';

interface MeetingSummaryButtonProps {
    roomid: any;
}

export const MeetingSummaryButton: FC<MeetingSummaryButtonProps> = props => {
    const { roomid } = props;
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
            className={`bg-[#fff] text-[#999999]   items-center justify-center rounded-[8px] ${
                disabled ? 'cursor-pointer hover:text-[#1B64F3]' : 'cursor-no-drop'
            }`}
            style={{ boxShadow: '0px 0px 4px 0px rgba(0,0,0,0.1)' }}
        >
            <div
                className=" gap-x-[4px] flex items-center justify-center h-[40px] px-[20px]"
                onClick={() => {
                    if (disabled) {
                        setSummaryParams({
                            id: roomid,
                        });
                        setSummaryClick(false);
                    }
                }}
            >
                <FundProjectionScreenOutlined className="text-[16px]" />
                <span className="text-[14px]">
                    {intl.formatMessage({ id: 'app.chatroom.content.meetingSummary' })}
                </span>
            </div>
        </div>
    );
}; 