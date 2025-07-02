/*
 * @LastEditors: biz
 */
import React, { FC } from 'react';
import { useIntl } from '@umijs/max';
import { SmartLoadingAnimation } from './SmartLoadingAnimation';

interface WaitingReplyIndicatorProps {
    isVisible: boolean;
    animationType?: 'typing' | 'wave' | 'pulse' | 'spinner';
    enableAutoRotate?: boolean;
}

export const WaitingReplyIndicator: FC<WaitingReplyIndicatorProps> = ({ 
    isVisible, 
    animationType = 'pulse',
    enableAutoRotate = true
}) => {
    const intl = useIntl();
    
    if (!isVisible) {
        return null;
    }
    
    return (
        <div className="flex justify-start pb-4 max-w-[90%] min-w-[300px]">
            <div className="max-w-full">
                <div className="max-w-[90%] min-w-[200px] rounded-xl relative  from-blue-50 to-indigo-50 text-gray-800 border border-blue-200 p-4  transition-all duration-300 backdrop-blur-sm">
                    <div className="flex items-center gap-4">
                        <div className="flex-shrink-0 p-2 bg-white rounded-full shadow-sm">
                            <SmartLoadingAnimation 
                                initialType={animationType}
                                autoRotate={enableAutoRotate}
                                rotateInterval={4000}
                                size="medium"
                            />
                        </div>
                        <div className="flex flex-col">
                            <span className="text-gray-700 text-sm font-semibold">
                                {intl.formatMessage({ id: 'app.chatroom.waitingReply' })}
                            </span>
                            
                        </div>
                    </div>
                    {/* Subtle gradient overlay */}
                    <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-white/20 to-transparent pointer-events-none" />
                </div>
            </div>
        </div>
    );
}; 