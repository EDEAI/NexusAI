import DraggablePanel from '@/components/Panel/DraggablePanel';
import { memo, useState } from 'react';
import { BlockEnum } from '../../types';
import WorkFlowLeftMenu from '../Menu/WorkFlowLeftMenu';
import WorkflowTitle from '../WorkflowTitle';
import NodePanelContent from './components/NodePanelContent';
import { useMount } from 'ahooks';
import { log } from 'mermaid/dist/logger';

interface SearchNodeList {
    [BlockEnum.Agent]?: any;
    [BlockEnum.Skill]?: any;
    workflow?: any;
}

interface NodePanelProps {
    visibleTabs?: ('node' | 'agent' | 'tool' | 'skill' | 'workflow')[];
    defaultActiveTab?: string;
    showTeamSwitch?: boolean;
    workflowName?: string;
    workflowDesc?: string;
    publishStatus?: boolean;
    onWidthChange?: (width: number) => void;
    onItemClick?: (item: any, type?: string) => void;
}

interface ListItemProps {
    data: any;
    index: number;
    onDragStart: (event: React.DragEvent, type: string, item: any) => void;
    onItemClick: (item: any) => void;
    type: string;
    typeBadge?: {
        icon: string;
        tooltip: string;
        color: string;
    };
}

export default memo(
    ({
        visibleTabs,
        defaultActiveTab,
        showTeamSwitch = true,
        workflowName,
        workflowDesc,
        publishStatus,
        onWidthChange,
        onItemClick,
    }: NodePanelProps) => {
        const [isMinWidth, setIsMinWidth] = useState(false);
        const [isCollapsed, setIsCollapsed] = useState(false);

        return (
            <DraggablePanel
                dragDirection="right"
                minWidth={200}
                maxWidth={415}
                className="fixed left-0 top-16 bg-white shadow-md"
                defaultWidth={isCollapsed ? 100 : 315}
                onChange={(width, height) => {
                    requestAnimationFrame(() => {
                        setIsMinWidth(width < 100);
                        onWidthChange?.(width);
                        const containers = document.querySelectorAll('.overflow-y-auto');
                        containers.forEach(container => {
                            if (container instanceof HTMLElement) {
                                const height = container.clientHeight;
                                const event = new CustomEvent('containerResize', {
                                    detail: { height, width },
                                });
                                container.dispatchEvent(event);
                            }
                        });
                    });
                }}
            >
                <div className="h-[calc(100vh-110px)] flex flex-col relative">
                    <NodePanelContent
                        visibleTabs={visibleTabs}
                        defaultActiveTab={defaultActiveTab}
                        showTeamSwitch={showTeamSwitch}
                        isMinWidth={isMinWidth}
                        isCollapsed={isCollapsed}
                        onItemClick={onItemClick}
                    />
                    <WorkFlowLeftMenu />
                    <div className="absolute left-[calc(100%+80px)] top-0">
                        <WorkflowTitle
                            name={workflowName}
                            description={workflowDesc}
                            publishStatus={publishStatus}
                        />
                    </div>
                </div>
            </DraggablePanel>
        );
    },
);
