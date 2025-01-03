/*
 * @Author: wnagchi 1305bcd@gmail.com
 * @Date: 2024-12-30 17:31:04
 * @LastEditors: biz
 * @LastEditTime: 2025-01-03 09:50:13
 * @FilePath: \NexusAI_GITHUB\web\src\components\WorkFlow\components\DraggableList\index.tsx
 */
import { QuestionCircleOutlined } from '@ant-design/icons';
import { getLocale } from '@umijs/max';
import { Tooltip } from 'antd';
import React, { memo } from 'react';
import UserCon, { UserConProps } from '../UserCon';

interface DraggableListProps {
    list: any[];
    onDragStart: (event: React.DragEvent, nodeType: string, item: any) => void;
    type?: 'normal' | 'tools' | 'workflow';
    typeBadge?: UserConProps['typeBadge'];
    onItemClick?: (item: any) => void;
}

interface BaseNodeItemProps {
    item: {
        type: string;
        data: {
            title: string;
        };
        baseData?: {
            icon?: string;
        };
    };
    onDragStart: DraggableListProps['onDragStart'];
    typeBadge?: UserConProps['typeBadge'];
    onItemClick?: (item: any) => void;
}

interface WorkflowNodeItemProps {
    item: {
        type: string;
        baseData: {
            name: string;
            description: string;
            icon?: string;
            nickname?: string;
        };
    };
    onDragStart: DraggableListProps['onDragStart'];
    typeBadge?: UserConProps['typeBadge'];
    onItemClick?: (item: any) => void;
}

interface ToolNodeItemProps {
    tool: {
        identity?: {
            label: {
                [key: string]: string;
            };
        };
        description?: {
            human?: {
                [key: string]: string;
            };
        };
    };
    category: {
        type: string;
        identity?: {
            label: {
                [key: string]: string;
            };
            description: {
                [key: string]: string;
            };
            icon?: string;
        };
        tools: any[];
    };
    onDragStart: DraggableListProps['onDragStart'];
    typeBadge?: UserConProps['typeBadge'];
    onItemClick?: (category: any, item: any, categoryIndex: number, toolIndex: number) => void;
    categoryIndex: number;
    toolIndex: number;
}

interface ToolCategoryProps {
    category: {
        identity?: {
            label: {
                [key: string]: string;
            };
            description: {
                [key: string]: string;
            };
            icon?: string;
        };
        tools: any[];
    };
    onDragStart: DraggableListProps['onDragStart'];
    typeBadge: UserConProps['typeBadge'];
    onItemClick?: (category: any, item: any, categoryIndex: number, toolIndex: number) => void;
    categoryIndex: number;
}

interface ToolNodeListProps {
    list: ToolCategoryProps['category'][];
    onDragStart: DraggableListProps['onDragStart'];
    typeBadge: UserConProps['typeBadge'];
    onItemClick?: (item: any) => void;
}

interface NodeWrapperProps {
    children: React.ReactNode;
    onDragStart: DraggableListProps['onDragStart'];
    onClick?: () => void;
    type: string;
    item: any;
}

// 新增 NodeWrapper 组件
const NodeWrapper = memo(({ children, onDragStart, onClick, type, item }: NodeWrapperProps) => (
    <div
        draggable
        onDragStart={e => onDragStart(e, type, item)}
        onClick={onClick}
        className="cursor-pointer hover:bg-blue-100 rounded-md px-2 box-border"
    >
        {children}
    </div>
));

// 修改 BaseNodeItem
const BaseNodeItem = memo(({ item, onDragStart, typeBadge, onItemClick }: BaseNodeItemProps & { onItemClick?: (item: any) => void }) => (
    <Tooltip placement="right" title={item?.baseData?.description}>
        <div>
            <NodeWrapper 
                onDragStart={onDragStart} 
                type={item.type} 
                item={item}
                onClick={() => onItemClick?.(item)}
            >
                <UserCon
                    title={item.data.title}
                    icon={item?.baseData?.icon || item.type}
                    typeBadge={typeBadge}
                />
            </NodeWrapper>
        </div>
    </Tooltip>
));

// 修改 WorkflowNodeItem
const WorkflowNodeItem = memo(({ item, onDragStart, typeBadge, onItemClick }: WorkflowNodeItemProps & { onItemClick?: (item: any) => void }) => (
    <Tooltip placement="right" title={item.baseData?.description}>
        <div>
            <NodeWrapper 
                onDragStart={onDragStart} 
                type={item.type} 
                item={item}
                onClick={() => onItemClick?.(item)}
            >
                <UserCon
                    title={item.baseData.name}
                    // desc={item.baseData.description}
                    icon={item.baseData.icon || 'workflow'}
                    extra={<div className="text-xs text-gray-500">{item.baseData.nickname}</div>}
                    typeBadge={typeBadge}
                />
            </NodeWrapper>
        </div>
    </Tooltip>
));

// 修改 ToolNodeItem
const ToolNodeItem = memo(({ 
    tool, 
    category, 
    onDragStart, 
    typeBadge,
    onItemClick,
    categoryIndex,
    toolIndex 
}: ToolNodeItemProps) => {
    const lang = getLocale() === 'en-US' ? 'en_US' : 'zh_Hans';

    return (
        <Tooltip placement="right" title={tool?.description?.human?.[lang]}>
            <div>
                <NodeWrapper 
                    onDragStart={onDragStart} 
                    type={category.type} 
                    item={category}
                    onClick={() => onItemClick?.(category, tool, categoryIndex, toolIndex)}
                >
                    <UserCon
                        title={tool?.identity?.label[lang]}
                        icon={category?.identity?.icon}
                        typeBadge={typeBadge}
                    />
                </NodeWrapper>
            </div>
        </Tooltip>
    );
});

// 修改 ToolCategory
const ToolCategory = memo(({ 
    category, 
    onDragStart, 
    typeBadge,
    onItemClick,
    categoryIndex 
}: ToolCategoryProps) => {
    const lang = getLocale() === 'en-US' ? 'en_US' : 'zh_Hans';

    return (
        <div>
            <div className="text-[#333333] mb-2">
                {category?.identity?.label[lang]}
                <Tooltip placement="right" title={category?.identity?.description[lang]}>
                    <QuestionCircleOutlined className="cursor-pointer ml-1" />
                </Tooltip>
            </div>
            {category.tools.map((tool, toolIndex) => (
                <ToolNodeItem
                    key={toolIndex}
                    tool={tool}
                    category={category}
                    onDragStart={onDragStart}
                    typeBadge={typeBadge}
                    onItemClick={(category, item, catIndex, toolIdx) => onItemClick?.(category, item, catIndex, toolIdx)}
                    categoryIndex={categoryIndex}
                    toolIndex={toolIndex}
                />
            ))}
        </div>
    );
});

// 修改 ToolNodeList
const ToolNodeList = memo(({ list, onDragStart, typeBadge, onItemClick }: ToolNodeListProps) => (
    <>
        {list.map((category, categoryIndex) => (
            <ToolCategory
                key={categoryIndex}
                category={category}
                typeBadge={typeBadge}
                onDragStart={onDragStart}
                onItemClick={onItemClick}
                categoryIndex={categoryIndex}
            />
        ))}
    </>
));

const DraggableList: React.FC<DraggableListProps> = ({
    list,
    onDragStart,
    type = 'normal',
    typeBadge = null,
    onItemClick
}) => {
    if (!list?.length) return null;

    return (
        <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-y-2 gap-2">
            {type === 'tools' ? (
                <ToolNodeList 
                    typeBadge={typeBadge} 
                    list={list} 
                    onDragStart={onDragStart}
                    onItemClick={onItemClick}
                />
            ) : type === 'workflow' ? (
                list.map((item, index) => (
                    <WorkflowNodeItem
                        key={index}
                        item={item}
                        onDragStart={onDragStart}
                        typeBadge={typeBadge}
                        onItemClick={onItemClick}
                    />
                ))
            ) : (
                list.map((item, index) => (
                    <BaseNodeItem
                        key={index}
                        item={item}
                        onDragStart={onDragStart}
                        typeBadge={typeBadge}
                        onItemClick={onItemClick}
                    />
                ))
            )}
        </div>
    );
};

export default memo(DraggableList);
