/*
 * @LastEditors: biz
 */
import { useResizePanel } from '@/components/WorkFlow/hooks/use-resize-panel';
import React, { memo, useCallback, useState } from 'react';

interface ResizablePanelProps {
    children: React.ReactNode;
    className?: string;
    dragDirection?: 'left' | 'right';
    minWidth?: number;
    maxWidth?: number;
    defaultWidth?: number;
}

const ResizablePanel: React.FC<ResizablePanelProps> = ({
    children,
    className = '',
    dragDirection = 'left',
    minWidth = 415,
    maxWidth = 820,
    defaultWidth = 415,
}) => {
    const [panelWidth, setPanelWidth] = useState<number>(defaultWidth);

    const handleResize = useCallback(
        (width: number) => {
            setPanelWidth(width);
        },
        [setPanelWidth],
    );

    const { triggerRef, containerRef } = useResizePanel({
        direction: 'horizontal',
        triggerDirection:dragDirection,
        minWidth,
        maxWidth,
        onResize: handleResize,
    });

    return (
        <div
            ref={containerRef}
            style={{ width: `${panelWidth}px` }}
            className={`flex flex-col p-4 shadow-lg rounded-md border border-blue-300 bg-white z-10 wrapPanel ${className}`}
        >
            {dragDirection === 'left' && (
                <div
                    ref={triggerRef}
                    className="absolute top-1/2 -translate-y-1/2 -left-2 w-3 h-6 cursor-col-resize resize-x"
                >
                    <div className="w-1 h-6 bg-gray-300 rounded-sm"></div>
                </div>
            )}
            {dragDirection === 'right' && (
                <div
                    ref={triggerRef}
                    className="absolute top-1/2 -translate-y-1/2 -right-2 flex justify-end w-3 h-6 cursor-col-resize resize-x"
                >
                    <div className="w-1 h-6 bg-gray-300 rounded-sm"></div>
                </div>
            )}
            {children}
        </div>
    );
};

export default memo(ResizablePanel);
