import { getAppListByMode } from '@/api/workflow';
import DraggablePanel from '@/components/Panel/DraggablePanel';
import { TagSelect, useTags } from '@/components/TagSearch';
import { SearchOutlined } from '@ant-design/icons';
import { ProForm, ProFormItem, ProFormRadio, ProFormText } from '@ant-design/pro-components';
import { getLocale, useIntl } from '@umijs/max';
import { useSetState } from 'ahooks';
import { Tabs, TabsProps } from 'antd';
import Fuse from 'fuse.js';
import { debounce } from 'lodash';
import { memo, useCallback, useEffect, useMemo, useState } from 'react';
import { getBaseNode } from '../../nodes/nodeDisperse';
import useStore from '../../store';
import { BlockEnum, TabConfig } from '../../types';
import DraggableList from '../DraggableList';

interface SearchNodeList {
    [BlockEnum.Agent]?: any;
    [BlockEnum.Skill]?: any;
    workflow?: any;
}

interface NodePanelProps {
    visibleTabs?: ('node' | 'agent' | 'tool' | 'skill' | 'workflow')[];
    defaultActiveTab?: string;
    showTeamSwitch?: boolean;
}

export default memo(({ visibleTabs, defaultActiveTab, showTeamSwitch = true }: NodePanelProps) => {
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
    const { tagList } = useTags();
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

    const toolData = useStore(state => state.toolData);

    useEffect(() => {
        setSearchTools(toolData?.list || []);
    }, [toolData]);

    const onDragStart = useCallback((event, nodeType, item) => {
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
        ({ tabIndex }) => {
            const currentConfig = tabConfigs.find(config => config.key === tabIndex);
            const [list, setList] = useState([]);

            useEffect(() => {
                const fetchData = async () => {
                    const data = await currentConfig.getData();
                    setList(data || []);
                };
                fetchData();
            }, [currentConfig, filterData]);

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

            return (
                <div className="overflow-y-auto">
                    <DraggableList
                        typeBadge={filterData?.keyword && currentConfig.tabKey != 'node' && {
                            icon: `/icons/${currentConfig.tabKey}.svg`,
                            tooltip: currentConfig.tabKey,
                            color: '#1b64f3',
                        }}
                        list={list}
                        onDragStart={onDragStart}
                        type={currentConfig.type}
                        onItemClick={handleItemClick}
                    />
                </div>
            );
        },
        [tabIndex, filterData]
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
            minWidth={70}
            className="fixed left-0 top-16 bg-white shadow-md"
        >
            <div className="h-[calc(100vh-110px)] flex flex-col">
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
                                    defaultMessage: '列表',
                                })}
                                <ProFormRadio.Group
                                    name="team"
                                    fieldProps={{
                                        options: [
                                            {
                                                label: intl.formatMessage({
                                                    id: 'workflow.team',
                                                    defaultMessage: '团队',
                                                }),
                                                value: 2,
                                            },
                                            {
                                                label: intl.formatMessage({
                                                    id: 'workflow.mine',
                                                    defaultMessage: '我的',
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
                                    defaultMessage: '搜索节点',
                                }),
                            }}
                            name="keyword"
                        />
                        <div className="w-full">
                            <ProFormItem name={'tag'}>
                                <TagSelect
                                    className="w-full"
                                    options={tagList}
                                    allowClear
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
                <div className="flex-1 overflow-y-auto">
                    {filterData?.keyword ? (
                        tabConfigs.map((item, index) => (
                            <RenderNodeList tabIndex={index + 1 + ''} />
                        ))
                    ) : (
                        <RenderNodeList tabIndex={tabIndex} />
                    )}
                </div>
            </div>
        </DraggablePanel>
    );
});
