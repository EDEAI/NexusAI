/*
 * @LastEditors: biz
 */
import React, { FC, useState, useEffect } from 'react';
import { LoadingAnimation } from './LoadingAnimation';

interface SmartLoadingAnimationProps {
    autoRotate?: boolean;
    rotateInterval?: number;
    initialType?: 'typing' | 'wave' | 'pulse' | 'spinner';
    size?: 'small' | 'medium' | 'large';
}

export const SmartLoadingAnimation: FC<SmartLoadingAnimationProps> = ({ 
    autoRotate = false,
    rotateInterval = 3000,
    initialType = 'wave',
    size = 'medium'
}) => {
    const [currentType, setCurrentType] = useState<'typing' | 'wave' | 'pulse' | 'spinner'>(initialType);
    const animationTypes: ('typing' | 'wave' | 'pulse' | 'spinner')[] = ['typing', 'wave', 'pulse', 'spinner'];

    // useEffect(() => {
    //     if (!autoRotate) return;

    //     const interval = setInterval(() => {
    //         setCurrentType(prev => {
    //             const currentIndex = animationTypes.indexOf(prev);
    //             const nextIndex = (currentIndex + 1) % animationTypes.length;
    //             return animationTypes[nextIndex];
    //         });
    //     }, rotateInterval);

    //     return () => clearInterval(interval);
    // }, [autoRotate, rotateInterval]);

    return (
        <div className="transition-all duration-500 ease-in-out">
            <LoadingAnimation type={currentType} size={size} />
        </div>
    );
}; 