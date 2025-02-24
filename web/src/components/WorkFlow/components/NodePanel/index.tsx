import { getAppListByMode } from '@/api/workflow';
import DraggablePanel from '@/components/Panel/DraggablePanel';
import { TagSelect } from '@/components/TagSearch';
import { SearchOutlined, MenuUnfoldOutlined, MenuFoldOutlined } from '@ant-design/icons';
import { ProForm, ProFormItem, ProFormRadio, ProFormText } from '@ant-design/pro-components';
import { getLocale, useIntl } from '@umijs/max';
import { useSetState } from 'ahooks';
import { Tabs, TabsProps, Spin } from 'antd';
import VirtualList from 'rc-virtual-list';
import Fuse from 'fuse.js';
import { debounce } from 'lodash';
import { memo, useCallback, useEffect, useMemo, useState, useRef } from 'react';
import { getBaseNode } from '../../nodes/nodeDisperse';
import useStore from '../../store';
import { BlockEnum, TabConfig } from '../../types';
import DraggableList from './components/DraggableList';
import { useTagStore } from '@/store/tags';
import WorkFlowLeftMenu from '../Menu/WorkFlowLeftMenu';
import WorkflowTitle from '../WorkflowTitle';

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

export default memo(({
    visibleTabs,
    defaultActiveTab,
    showTeamSwitch = true,
    workflowName,
    workflowDesc,
    publishStatus,
    onWidthChange
}: NodePanelProps) => {
    const intl = useIntl();
    const lang = getLocale() == 'en-US' ? 'en_US' : 'zh_Hans';
    const originNodes = getBaseNode();
    const baseNodes = Object.values(originNodes)
        .filter(
            item =>
                ![BlockEnum.Start, BlockEnum.Agent, BlockEnum.Tool, BlockEnum.Skill].includes(
                    item.base.type,
                ),
        )
        .map(item => item.base);

    const [tabIndex, setTabIndex] = useState(defaultActiveTab || '1');
    const [searchNode, setSearchNode] = useState(baseNodes);
    const [searchTools, setSearchTools] = useState([]);
    const { tags } = useTagStore();
    const [searchNodeList, setSearchNodeList] = useSetState<SearchNodeList>({
        [BlockEnum.Agent]: [],
        [BlockEnum.Skill]: [],
        ['workflow']: [],
    });
    const [filterData, setFilterData] = useState({
        team: 1,
        keyword: '',
        tag: [],
    });
    const [isMinWidth, setIsMinWidth] = useState(false);
    const [isCollapsed, setIsCollapsed] = useState(false);

    const toolData = useStore(state => state.toolData);

    useEffect(() => {
        setSearchTools(toolData?.list || []);
    }, [toolData]);

    const onDragStart = useCallback((event, nodeType, item) => {
        console.log('onDragStart', event, nodeType, item);
        event.dataTransfer.setData(
            'application/reactflow',
            JSON.stringify({ type: nodeType, item }),
        );
        event.dataTransfer.effectAllowed = 'move';
    }, []);

    const searchNodesByKeyword = useCallback((nodes: any[], keyword: string) => {
        if (!keyword) return nodes;

        const fuse = new Fuse(nodes, {
            keys: ['data.title', 'type', 'data.desc'],
            threshold: 0.3,
            includeScore: true,
        });

        const results = fuse.search(keyword);
        return results.map(result => result.item);
    }, []);

    const searchToolsByKeyword = useCallback(
        (tools: any[], keyword: string) => {
            if (!keyword) return tools;

            const flattenedTools = tools.map(category => ({
                ...category,
                tools: category.tools?.map(tool => ({
                    ...tool,
                    categoryName: category.identity?.label?.[lang],
                    categoryIcon: category.identity?.icon,
                })),
            }));

            const fuse = new Fuse(flattenedTools, {
                keys: [
                    'identity.label.zh_Hans',
                    'identity.label.en_US',
                    'identity.description.zh_Hans',
                    'identity.description.en_US',
                    'tools.identity.label.zh_Hans',
                    'tools.identity.label.en_US',
                    'tools.description.human.zh_Hans',
                    'tools.description.human.en_US',
                ],
                threshold: 0.4,
                includeScore: true,
                useExtendedSearch: true,
            });

            const results = fuse.search(keyword);

            return results
                .map(result => ({
                    ...result.item,
                    tools: result.item.tools.filter(tool => {
                        const toolFuse = new Fuse([tool], {
                            keys: [
                                'identity.label.zh_Hans',
                                'identity.label.en_US',
                                'description.human.zh_Hans',
                                'description.human.en_US',
                            ],
                            threshold: 0.4,
                        });
                        return toolFuse.search(keyword).length > 0;
                    }),
                }))
                .filter(item => item.tools.length > 0);
        },
        [lang],
    );

    const tabConfigs: TabConfig[] = useMemo(() => {
        const allTabs: TabConfig[] = [
            {
                tabKey: 'node' as const,
                label: 'workflow.node',
                defaultMessage: 'Node',
                type: 'normal' as const,
                getData: () =>
                    filterData.keyword
                        ? searchNodesByKeyword(searchNode, filterData.keyword)
                        : searchNode,
            },
            {
                tabKey: 'agent' as const,
                label: 'workflow.agent',
                defaultMessage: 'Agent',
                type: 'normal' as const,
                getData: () => getAppsData(BlockEnum.Agent),
            },
            {
                tabKey: 'tool' as const,
                label: 'workflow.tool',
                defaultMessage: 'Tool',
                type: 'tools' as const,
                getData: () =>
                    filterData.keyword
                        ? searchToolsByKeyword(searchTools, filterData.keyword)
                        : searchTools,
            },
            {
                tabKey: 'skill' as const,
                label: 'workflow.skill',
                defaultMessage: 'Skill',
                type: 'normal' as const,
                getData: async () => await getAppsData(BlockEnum.Skill),
            },
            {
                tabKey: 'workflow' as const,
                label: 'workflow.list',
                defaultMessage: 'Workflow',
                type: 'workflow' as const,
                getData: async () => await getAppsData('workflow'),
            },
        ];
        const tabList = visibleTabs?.length
            ? allTabs.filter(tab => visibleTabs.includes(tab.tabKey))
            : allTabs;

        return tabList.map((item, index) => {
            return { ...item, key: index + 1 + '' };
        });
    }, [
        searchNode,
        searchNodeList,
        searchTools,
        visibleTabs,
        filterData,
        searchNodesByKeyword,
        searchToolsByKeyword,
    ]);

    const tabItems: TabsProps['items'] = useMemo(
        () =>
            tabConfigs.map((config, index) => ({
                key: config.key,
                label: intl.formatMessage({
                    id: config.label,
                    defaultMessage: config.defaultMessage,
                }),
            })),
        [tabConfigs],
    );

    const RenderNodeList = useCallback(
        ({ tabIndex, showName = true }) => {
            const currentConfig = tabConfigs.find(config => config.key === tabIndex);
            const [list, setList] = useState<any[]>([]);
            const [loading, setLoading] = useState(true);
            const [displayList, setDisplayList] = useState<any[]>([]);
            const [pageSize] = useState(20);
            const [containerHeight, setContainerHeight] = useState(500);
            const containerRef = useRef<HTMLDivElement>(null);
            const itemHeight = 54;

            useEffect(() => {
                const updateContainerHeight = () => {
                    if (containerRef.current) {
                        const height = containerRef.current.clientHeight;
                        setContainerHeight(height);
                    }
                };

                const handleResize = (e: CustomEvent) => {
                    setContainerHeight(e.detail.height);
                };

                updateContainerHeight();

                if (containerRef.current) {
                    containerRef.current.addEventListener('containerResize', handleResize as EventListener);
                }

                window.addEventListener('resize', updateContainerHeight);

                return () => {
                    if (containerRef.current) {
                        containerRef.current.removeEventListener('containerResize', handleResize as EventListener);
                    }
                    window.removeEventListener('resize', updateContainerHeight);
                };
            }, []);

            useEffect(() => {
                const fetchData = async () => {
                    setLoading(true);
                    try {
                        const data = await currentConfig.getData();
                        const processedData = data?.map((item: any, index: number) => ({
                            ...item,
                            id: `${currentConfig.tabKey}-${index}`,
                        })) || [];
                        setList(processedData);
                        setDisplayList(processedData.slice(0, pageSize));
                    } catch (error) {
                        console.error('Failed to fetch data:', error);
                    } finally {
                        setLoading(false);
                    }
                };
                fetchData();
            }, [currentConfig, filterData]);

            const onScroll = (e: React.UIEvent<HTMLElement, UIEvent>) => {
                if (e.currentTarget.scrollHeight - e.currentTarget.scrollTop === containerHeight) {
                    const currentLength = displayList.length;
                    if (currentLength < list.length) {
                        const nextItems = list.slice(currentLength, currentLength + pageSize);
                        setDisplayList(prev => [...prev, ...nextItems]);
                    }
                }
            };

            const handleItemClick = useCallback((category: any, item: any, categoryIndex?: number, toolIndex?: number) => {
                console.log('Clicked category:', category);
                console.log('Clicked item:', item);
                console.log('Indices:', categoryIndex, toolIndex);

                switch(currentConfig.tabKey) {
                    case 'tool':
                        if (categoryIndex !== undefined && toolIndex !== undefined) {
                            console.log(`Tool ${item.identity?.label[lang]} in category ${category.identity?.label[lang]}`);
                        }
                        break;
                    case 'workflow':

                        break;
                    case 'agent':

                        break;
                }
            }, [currentConfig.tabKey, lang]);

            const ListItem = memo(({ data, index, onDragStart, onItemClick, type, typeBadge }: ListItemProps) => (
                <DraggableList
                    typeBadge={typeBadge}
                    list={[data]}
                    onDragStart={onDragStart}
                    type={type}
                    onItemClick={(item) => onItemClick(item)}
                />
            ));

            return (
                <div ref={containerRef} className="overflow-y-auto h-full">
                    <Spin spinning={loading}>
                        {filterData?.keyword ? (
                            <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-2">
                                {displayList.map((item) => (
                                    <ListItem
                                        key={item.id}
                                        data={item}
                                        index={displayList.indexOf(item)}
                                        onDragStart={onDragStart}
                                        onItemClick={handleItemClick}
                                        type={currentConfig.type}
                                        typeBadge={filterData?.keyword && currentConfig.tabKey != 'node' ? {
                                            icon: `/icons/${currentConfig.tabKey}.svg`,
                                            tooltip: currentConfig.tabKey,
                                            color: '#1b64f3',
                                        } : undefined}
                                    />
                                ))}
                            </div>
                        ) : (
                            <VirtualList
                                data={displayList}
                                height={containerHeight}
                                itemHeight={itemHeight}
                                itemKey="id"
                                onScroll={onScroll}
                            >
                                {(item) => (
                                    <ListItem
                                        data={item}
                                        index={displayList.indexOf(item)}
                                        onDragStart={onDragStart}
                                        onItemClick={handleItemClick}
                                        type={currentConfig.type}
                                        typeBadge={filterData?.keyword && currentConfig.tabKey != 'node' ? {
                                            icon: `/icons/${currentConfig.tabKey}.svg`,
                                            tooltip: currentConfig.tabKey,
                                            color: '#1b64f3',
                                        } : undefined}
                                    />
                                )}
                            </VirtualList>
                        )}
                    </Spin>
                </div>
            );
        },
        [tabIndex, filterData, isMinWidth]
    );

    const getAppsData = useCallback(
        async (nodeType: BlockEnum.Agent | BlockEnum.Skill | 'workflow') => {
            try {
                const resData = await getAppListByMode(nodeType, {
                    search_type: filterData.team,
                    apps_name: filterData.keyword,
                    tag_ids: filterData.tag?.join(',') || '',
                });
                if (resData?.code === 0 && resData?.data?.list?.length) {
                    const list = resData.data.list.map(item => ({
                        ...originNodes[nodeType]?.base,
                        data: {
                            ...originNodes[nodeType]?.base.data,
                            title: item.name,
                            desc: item.description,
                        },
                        baseData: item,
                    }));
                    setSearchNodeList({ [nodeType]: list });
                    return list;
                }
            } catch (error) {
                console.error(`Failed to fetch ${nodeType} data:`, error);
            }
        },
        [filterData],
    );

    const debouncedSetFilter = useCallback(
        debounce(values => {
            setFilterData(values);
        }, 500),
        [],
    );

    const onFilterChange = useCallback(
        (changedValues, allValues) => {
            if ('team' in changedValues) {
                setFilterData(allValues);
                if (allValues.team == 2) {
                }
            } else if ('tag' in changedValues || 'keyword' in changedValues) {
                debouncedSetFilter(allValues);
            }
        },
        [debouncedSetFilter],
    );

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
                    // if (width < 100 && !isCollapsed) {
                    //     setIsCollapsed(true);
                    // }
                    onWidthChange?.(width);
                    const containers = document.querySelectorAll('.overflow-y-auto');
                    containers.forEach((container) => {
                        if (container instanceof HTMLElement) {
                            const height = container.clientHeight;
                            const event = new CustomEvent('containerResize', {
                                detail: { height, width }
                            });
                            container.dispatchEvent(event);
                        }
                    });
                });
            }}
        >
            <div className="h-[calc(100vh-110px)] flex flex-col relative">

                {!isCollapsed && (
                    <div className="px-4 py-3">
                        <ProForm
                            submitter={false}
                            initialValues={filterData}
                            onValuesChange={onFilterChange}
                        >
                            {showTeamSwitch && (
                                <div className="flex gap-2 items-center text-base mb-4">
                                    {intl.formatMessage({
                                        id: 'workflow.nodeList',
                                        defaultMessage: '',
                                    })}
                                    <ProFormRadio.Group
                                        name="team"
                                        fieldProps={{
                                            options: [
                                                {
                                                    label: intl.formatMessage({
                                                        id: 'workflow.team',
                                                        defaultMessage: '',
                                                    }),
                                                    value: 2,
                                                },
                                                {
                                                    label: intl.formatMessage({
                                                        id: 'workflow.mine',
                                                        defaultMessage: '',
                                                    }),
                                                    value: 1,
                                                },
                                            ],
                                            size: 'small',
                                            optionType: 'button',
                                            buttonStyle: 'solid',
                                        }}
                                        formItemProps={{ className: 'mb-0' }}
                                    />
                                </div>
                            )}

                            <ProFormText
                                fieldProps={{
                                    prefix: <SearchOutlined />,
                                    placeholder: intl.formatMessage({
                                        id: 'workflow.search',
                                        defaultMessage: '',
                                    }),
                                }}
                                name="keyword"
                            />
                            <div className="w-full">
                                <ProFormItem name={'tag'}>
                                    <TagSelect
                                        className="w-full"
                                        options={tags}
                                        listStyle={isMinWidth?'horizontal':'vertical'}
                                        allowClear
                                        placeholder={intl.formatMessage({
                                            id: 'creation.placeholder.selectTags',
                                            defaultMessage: '',
                                        })}
                                        onChange={e => {}}
                                    ></TagSelect>
                                </ProFormItem>
                            </div>
                        </ProForm>
                        {filterData?.keyword ? null : (
                            <Tabs
                                activeKey={tabIndex}
                                items={tabItems}
                                onChange={key => {
                                    setTabIndex(key);
                                }}
                            />
                        )}
                    </div>
                )}
                <div className="flex-1 overflow-y-auto">
                    {filterData?.keyword ? (
                        <div className="grid gap-4">
                            {tabConfigs.map((item, index) => (
                                <div key={item.key} className="space-y-2">
                                    {!isCollapsed && (
                                        <div className="text-base font-medium px-2">
                                            {intl.formatMessage({
                                                id: item.label,
                                                defaultMessage: item.defaultMessage,
                                            })}
                                        </div>
                                    )}
                                    <RenderNodeList
                                        key={item.key}
                                        tabIndex={index + 1 + ''}
                                        showName={!isMinWidth}
                                    />
                                </div>
                            ))}
                        </div>
                    ) : (
                        <RenderNodeList
                            tabIndex={tabIndex}
                            showName={!isMinWidth}
                        />
                    )}
                </div>
                <WorkFlowLeftMenu></WorkFlowLeftMenu>
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
});
