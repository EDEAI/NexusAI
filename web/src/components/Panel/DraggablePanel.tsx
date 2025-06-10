/*
 * @LastEditors: biz
 */
import { useResizePanel } from '@/components/WorkFlow/hooks/use-resize-panel';
import React, { memo, useCallback, useState } from 'react';

interface ResizablePanelProps {
    children: React.ReactNode;
    className?: string;
    dragDirection?: 'left' | 'right' | 'top' | 'bottom';
    minWidth?: number;
    maxWidth?: number;
    minHeight?: number;
    maxHeight?: number;
    defaultWidth?: number;
    defaultHeight?: number;
    onChange?: (width: number, height: number) => void;
}

const ResizablePanel: React.FC<ResizablePanelProps> = ({
    children,
    className = '',
    dragDirection = 'left',
    minWidth = 115,
    maxWidth = 820,
    minHeight = 200,
    maxHeight = 800,
    defaultWidth = 415,
    defaultHeight = 300,
    onChange,
}) => {
    const [panelWidth, setPanelWidth] = useState<number>(defaultWidth);
    const [panelHeight, setPanelHeight] = useState<number>(defaultHeight);

    const handleResize = useCallback(
        (width: number, height: number) => {
            setPanelWidth(width);
            if (height) setPanelHeight(height);
            onChange?.(width, height);
        },
        [setPanelWidth, setPanelHeight, onChange],
    );

    const { triggerRef, containerRef } = useResizePanel({
        direction: ['left', 'right'].includes(dragDirection) ? 'horizontal' : 'vertical',
        triggerDirection: dragDirection,
        minWidth,
        maxWidth,
        minHeight,
        maxHeight,
        onResize: handleResize,
    });

    return (
        <div
            ref={containerRef}
            style={{
                width: ['left', 'right'].includes(dragDirection) ? `${panelWidth}px` : undefined,
                height: ['top', 'bottom'].includes(dragDirection) ? `${panelHeight}px` : undefined
            }}
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
            {dragDirection === 'top' && (
                <div
                    ref={triggerRef}
                    className="absolute left-1/2 -translate-x-1/2 -top-2 h-3 w-6 cursor-row-resize resize-y"
                >
                    <div className="h-1 w-6 bg-gray-300 rounded-sm"></div>
                </div>
            )}
            {dragDirection === 'bottom' && (
                <div
                    ref={triggerRef}
                    className="absolute left-1/2 -translate-x-1/2 -bottom-2 h-3 w-6 cursor-row-resize resize-y"
                >
                    <div className="h-1 w-6 bg-gray-300 rounded-sm"></div>
                </div>
            )}
            {children}
        </div>
    );
};

export default memo(ResizablePanel);
