/*
 * @LastEditors: biz
 */
import React, { FC } from 'react';

interface LoadingAnimationProps {
    type?: 'typing' | 'wave' | 'pulse' | 'spinner';
    size?: 'small' | 'medium' | 'large';
}

export const LoadingAnimation: FC<LoadingAnimationProps> = ({ 
    type = 'typing', 
    size = 'medium' 
}) => {
    // Typing animation - three bouncing dots with enhanced styling
    if (type === 'typing') {
        return (
            <>
                <style>
                    {`
                        @keyframes chatroom-typing-bounce {
                            0%, 60%, 100% {
                                transform: translateY(0);
                                opacity: 0.7;
                            }
                            30% {
                                transform: translateY(-8px);
                                opacity: 1;
                            }
                        }
                    `}
                </style>
                <div className="flex items-center justify-center space-x-1.5">
                    <div 
                        className="w-2.5 h-2.5 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full shadow-sm"
                        style={{ 
                            animation: 'chatroom-typing-bounce 1.4s ease-in-out infinite',
                            animationDelay: '0s'
                        }}
                    />
                    <div 
                        className="w-2.5 h-2.5 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full shadow-sm"
                        style={{ 
                            animation: 'chatroom-typing-bounce 1.4s ease-in-out infinite',
                            animationDelay: '0.2s'
                        }}
                    />
                    <div 
                        className="w-2.5 h-2.5 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full shadow-sm"
                        style={{ 
                            animation: 'chatroom-typing-bounce 1.4s ease-in-out infinite',
                            animationDelay: '0.4s'
                        }}
                    />
                </div>
            </>
        );
    }

    // Wave animation - animated bars
    if (type === 'wave') {
        const barStyle: React.CSSProperties = {
            animation: 'chatroom-wave 1.2s ease-in-out infinite',
            transformOrigin: 'bottom'
        };

        return (
            <>
                <style>
                    {`
                        @keyframes chatroom-wave {
                            0%, 40%, 100% { transform: scaleY(0.4); }
                            20% { transform: scaleY(1); }
                        }
                    `}
                </style>
                <div className="flex items-end justify-center space-x-1">
                    {[0, 0.1, 0.2, 0.3, 0.4].map((delay, i) => (
                        <div
                            key={i}
                            className="w-1 h-4 bg-gradient-to-t from-blue-600 to-blue-400 rounded-sm"
                            style={{
                                ...barStyle,
                                animationDelay: `${delay}s`
                            }}
                        />
                    ))}
                </div>
            </>
        );
    }

    // Pulse animation - expanding circles
    if (type === 'pulse') {
        return (
            <>
                <style>
                    {`
                        @keyframes chatroom-pulse-ring {
                            0% {
                                transform: scale(0.8);
                                opacity: 1;
                            }
                            100% {
                                transform: scale(2.4);
                                opacity: 0;
                            }
                        }
                        @keyframes chatroom-pulse-dot {
                            0% {
                                transform: scale(0.8);
                            }
                            50% {
                                transform: scale(1);
                            }
                            100% {
                                transform: scale(0.8);
                            }
                        }
                    `}
                </style>
                <div className="flex items-center justify-center relative w-8 h-8">
                    <div 
                        className="absolute w-3 h-3 bg-blue-500 rounded-full"
                        style={{ 
                            left: '50%', 
                            top: '50%', 
                            transform: 'translate(-50%, -50%)',
                            animation: 'chatroom-pulse-ring 1.5s ease-out infinite'
                        }}
                    />
                    <div 
                        className="absolute w-3 h-3 bg-blue-400 rounded-full"
                        style={{ 
                            left: '50%', 
                            top: '50%', 
                            transform: 'translate(-50%, -50%)',
                            animation: 'chatroom-pulse-ring 1.5s ease-out infinite',
                            animationDelay: '0.5s'
                        }}
                    />
                    <div 
                        className="w-3 h-3 bg-blue-600 rounded-full relative z-10"
                        style={{
                            animation: 'chatroom-pulse-dot 1.5s ease-in-out infinite'
                        }}
                    />
                </div>
            </>
        );
    }

    // Spinner animation - rotating gradient circle
    if (type === 'spinner') {
        return (
            <>
                <style>
                    {`
                        @keyframes chatroom-spin {
                            0% {
                                transform: rotate(0deg);
                            }
                            100% {
                                transform: rotate(360deg);
                            }
                        }
                    `}
                </style>
                <div className="flex items-center justify-center">
                    <div
                        className="border-4 border-blue-200 border-t-blue-600 rounded-full"
                        style={{
                            width: '20px',
                            height: '20px',
                            animation: 'chatroom-spin 1s linear infinite'
                        }}
                    />
                </div>
            </>
        );
    }

    return null;
}; 