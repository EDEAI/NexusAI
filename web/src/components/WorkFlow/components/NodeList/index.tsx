import React, { memo } from 'react';
import { Tooltip, Empty, Spin } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';
import UserCon from '../UserCon';
import { getLocale } from '@umijs/max';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface NodeItemProps {
    item: {
        type: string;
        data: {
            title: string;
            desc?: string;
        };
        baseData?: {
            icon?: string;
            name: string;
            description?: string;
        };
    };
    onDragStart: (event: React.DragEvent, type: string, item: any) => void;
}

export const NodeItem = memo(({ item, onDragStart }: NodeItemProps) => (
    <div
        onDragStart={event => onDragStart(event, item.type, item)}
        draggable
        className="cursor-pointer hover:bg-blue-100 rounded-md px-2 box-border"
    >
        <UserCon
            title={item.data.title}
            icon={item?.baseData?.icon || item.type}
        />
    </div>
));

interface ToolNodeItemProps extends NodeItemProps {
    description?: string;
}

const tooltipOverlayInnerStyle: React.CSSProperties = {
    maxHeight: 'min(60vh, 420px)',
    overflowY: 'auto',
    overflowX: 'hidden',
    maxWidth: 400,
};

const renderTooltipContent = (content?: string) => {
    if (!content) return null;
    return (
        <div className="workflow-tooltip-markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        </div>
    );
};

export const ToolNodeItem = memo(({ item, onDragStart, description }: ToolNodeItemProps) => (
    <Tooltip
        placement="right"
        title={renderTooltipContent(description)}
        overlayInnerStyle={tooltipOverlayInnerStyle}
    >
        <NodeItem item={item} onDragStart={onDragStart} />
    </Tooltip>
));

interface NodeListProps {
    loading?: boolean;
    items: any[];
    onDragStart: (event: React.DragEvent, type: string, item: any) => void;
    emptyText?: string;
    renderItem?: (item: any, index: number) => React.ReactNode;
}

export const NodeList = memo(({ 
    loading = false, 
    items = [], 
    onDragStart,
    emptyText = 'No data available',
    renderItem
}: NodeListProps) => {
    if (loading) {
        return <Spin className="w-full flex justify-center p-4" />;
    }

    if (!items.length) {
        return <Empty description={emptyText} />;
    }

    return (
        <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-y-2 gap-2">
            {renderItem ? 
                items.map((item, index) => renderItem(item, index)) :
                items.map((item, index) => (
                    <NodeItem key={index} item={item} onDragStart={onDragStart} />
                ))
            }
        </div>
    );
});

interface ToolsNodeListProps {
    items: any[];
    onDragStart: (event: React.DragEvent, type: string, item: any) => void;
}

export const ToolsNodeList = memo(({ items, onDragStart }: ToolsNodeListProps) => {
    const lang = getLocale() === 'en-US' ? 'en_US' : 'zh_Hans';
    
    return (
        <div>
            {items.map((category, index) => (
                <div key={index}>
                    <div className="text-[#333333] mb-2">
                        {category?.identity?.label[lang]}
                        <Tooltip
                            placement="right"
                            title={renderTooltipContent(category?.identity?.description[lang])}
                            overlayInnerStyle={tooltipOverlayInnerStyle}
                        >
                            <QuestionCircleOutlined className="cursor-pointer ml-1" />
                        </Tooltip>
                    </div>
                    {category.tools.map((tool, toolIndex) => (
                        <ToolNodeItem
                            key={toolIndex}
                            item={{
                                type: category.type,
                                data: {
                                    title: tool?.identity?.label[lang],
                                },
                                baseData: {
                                    icon: category?.identity?.icon,
                                }
                            }}
                            onDragStart={onDragStart}
                            description={tool?.description?.human?.[lang]}
                        />
                    ))}
                </div>
            ))}
        </div>
    );
});

export default NodeList;
