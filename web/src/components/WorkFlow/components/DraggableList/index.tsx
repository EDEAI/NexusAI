/*
 * @Author: wnagchi 1305bcd@gmail.com
 * @Date: 2024-12-30 17:31:04
 * @LastEditors: biz
 * @LastEditTime: 2024-12-31 16:44:13
 * @FilePath: \NexusAI_GITHUB\web\src\components\WorkFlow\components\DraggableList\index.tsx
 */
import React, { memo, useState, useCallback, useEffect, useMemo } from 'react';
import { Tooltip } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';
import { getLocale } from '@umijs/max';
import UserCon from '../UserCon';
import { useStore } from '@umijs/max';
import { getAgentList, getSkillList, getWorkflowList } from '@/api/workflow';
import { getBaseNode } from '../../nodes/nodeDisperse';
import { BlockEnum } from '../../types';

interface DraggableListProps {
    list: any[];
    onDragStart: (event: React.DragEvent, nodeType: string, item: any) => void;
    type?: 'normal' | 'tools' | 'workflow';
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
            icon?: string;
        };
    };
    onDragStart: DraggableListProps['onDragStart'];
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
}

interface ToolNodeListProps {
    list: ToolCategoryProps['category'][];
    onDragStart: DraggableListProps['onDragStart'];
}

interface FetchDataParams {
    type: 'node' | 'agent' | 'tool' | 'skill' | 'workflow';
    team: number;
    keyword?: string;
}

interface FetchDataResult {
    list: any[];
    total?: number;
}

const fetchTabData = async ({ type, team, keyword }: FetchDataParams): Promise<FetchDataResult> => {
    try {
        const teamStatus = team === 1 ? 3 : 2;
        let result: FetchDataResult = { list: [] };

        switch (type) {
            case 'agent':
                const agentRes = await getAgentList(teamStatus);
                if (agentRes?.code === 0) {
                    result.list = agentRes.data.list;
                }
                break;

            case 'skill':
                const skillRes = await getSkillList(teamStatus);
                if (skillRes?.code === 0) {
                    result.list = skillRes.data.list;
                }
                break;

            case 'workflow':
                const workflowRes = await getWorkflowList(team === 1 ? 1 : 2);
                if (workflowRes?.code === 0) {
                    result.list = workflowRes.data.list;
                }
                break;

            case 'tool':
                // 工具数据从 store 获取
                const toolData = useStore.getState().toolData;
                result.list = toolData?.list || [];
                break;

            case 'node':
                // 基础节点数据
                const originNodes = getBaseNode();
                result.list = Object.values(originNodes)
                    .filter(
                        item =>
                            ![BlockEnum.Start, BlockEnum.Agent, BlockEnum.Tool, BlockEnum.Skill].includes(
                                item.base.type,
                            ),
                    )
                    .map(item => item.base);
                break;
        }

        // 如果有关键字，进行过滤
        if (keyword) {
            result.list = result.list.filter(item => {
                const searchText = type === 'workflow' 
                    ? item.name 
                    : item.data?.title || item.baseData?.name || '';
                return searchText.toLowerCase().includes(keyword.toLowerCase());
            });
        }

        return result;
    } catch (error) {
        console.error(`Failed to fetch ${type} data:`, error);
        return { list: [] };
    }
};

// Base node renderer
const BaseNodeItem = memo(({ item, onDragStart }: BaseNodeItemProps) => (
    <div
        draggable
        onDragStart={(e) => onDragStart(e, item.type, item)}
        className="cursor-pointer hover:bg-blue-100 rounded-md px-2 box-border"
    >
        <UserCon
            title={item.data.title}
            icon={item?.baseData?.icon || item.type}
        />
    </div>
));

// Workflow node renderer
const WorkflowNodeItem = memo(({ item, onDragStart }: WorkflowNodeItemProps) => (
    <div
        draggable
        onDragStart={(e) => onDragStart(e, item.type, item)}
        className="cursor-pointer hover:bg-blue-100 rounded-md px-2 box-border"
    >
        <UserCon
            title={item.baseData.name}
            desc={item.baseData.description}
            icon={item.baseData.icon || 'workflow'}
            extra={
                <div className="text-xs text-gray-500">
                    {item.baseData.nickname}
                </div>
            }
        />
    </div>
));

// Tool node renderer
const ToolNodeItem = memo(({ tool, category, onDragStart }: ToolNodeItemProps) => {
    const lang = getLocale() === 'en-US' ? 'en_US' : 'zh_Hans';

    return (
        <Tooltip placement="right" title={tool?.description?.human?.[lang]}>
            <div
                draggable
                onDragStart={(e) => onDragStart(e, category.type, category)}
                className="cursor-pointer hover:bg-blue-100 rounded-md px-2 box-border"
            >
                <UserCon
                    title={tool?.identity?.label[lang]}
                    icon={category?.identity?.icon}
                />
            </div>
        </Tooltip>
    );
});

// Tool category renderer
const ToolCategory = memo(({ category, onDragStart }: ToolCategoryProps) => {
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
                />
            ))}
        </div>
    );
});

// Tool node list renderer
const ToolNodeList = memo(({ list, onDragStart }: ToolNodeListProps) => (
    <>
        {list.map((category, index) => (
            <ToolCategory
                key={index}
                category={category}
                onDragStart={onDragStart}
            />
        ))}
    </>
));

const DraggableList: React.FC<DraggableListProps> = ({ list, onDragStart, type = 'normal' }) => {
    if (!list?.length) return null;

    return (
        <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-y-2 gap-2">
            {type === 'tools' ? (
                <ToolNodeList list={list} onDragStart={onDragStart} />
            ) : type === 'workflow' ? (
                list.map((item, index) => (
                    <WorkflowNodeItem
                        key={index}
                        item={item}
                        onDragStart={onDragStart}
                    />
                ))
            ) : (
                list.map((item, index) => (
                    <BaseNodeItem
                        key={index}
                        item={item}
                        onDragStart={onDragStart}
                    />
                ))
            )}
        </div>
    );
};

export default memo(DraggableList);
