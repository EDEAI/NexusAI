import { getAgentList, getAppList, getSkillList, getWorkflowList } from '@/api/workflow';
import { SearchOutlined } from '@ant-design/icons';
import { ProForm, ProFormRadio, ProFormText } from '@ant-design/pro-components';
import { getLocale, useIntl } from '@umijs/max';
import { useSetState } from 'ahooks';
import { Tabs, TabsProps } from 'antd';
import { memo, useCallback, useEffect, useMemo, useState } from 'react';
import DraggablePanel from '../Panel/DraggablePanel';
import DraggableList from './components/DraggableList';
import { getBaseNode } from './nodes/nodeDisperse';
import useStore from './store';
import { BlockEnum, TabConfig } from './types';
import TagSearch from '../TagSearch';

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

    const [tabIndex, setTabIndex] = useState(defaultActiveTab);
    const [searchNode, setSearchNode] = useState(baseNodes);
    const [searchTools, setSearchTools] = useState([]);
    const [searchNodeList, setSearchNodeList] = useSetState<SearchNodeList>({
        [BlockEnum.Agent]: [],
        [BlockEnum.Skill]: [],
        ['workflow']: [],
    });
    const [filterData, setFilterData] = useState({
        team: 1,
        keyword: '',
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

    const tabConfigs: TabConfig[] = useMemo(() => {
        const allTabs: TabConfig[] = [
            {
                key: '1',
                tabKey: 'node' as const,
                label: 'workflow.node',
                defaultMessage: 'Node',
                type: 'normal' as const,
                getData: () => searchNode,
            },
            {
                key: '2',
                tabKey: 'agent' as const,
                label: 'workflow.agent',
                defaultMessage: 'Agent',
                type: 'normal' as const,
                getData: () => searchNodeList[BlockEnum.Agent],
            },
            {
                key: '3',
                tabKey: 'tool' as const,
                label: 'workflow.tool',
                defaultMessage: 'Tool',
                type: 'tools' as const,
                getData: () => searchTools,
            },
            {
                key: '4',
                tabKey: 'skill' as const,
                label: 'workflow.skill',
                defaultMessage: 'Skill',
                type: 'normal' as const,
                getData: () => searchNodeList[BlockEnum.Skill],
            },
            {
                key: '5',
                tabKey: 'workflow' as const,
                label: 'workflow.list',
                defaultMessage: 'Workflow',
                type: 'workflow' as const,
                getData: () => searchNodeList['workflow'],
            },
        ];
        const tabList = allTabs.map(tab => ({
            ...tab,
            show: !visibleTabs || visibleTabs.includes(tab.tabKey),
        }));

        if (!defaultActiveTab) {
            setTabIndex(tabList.filter(item => item.show)[0].key);
        }

        return tabList;
    }, [searchNode, searchNodeList, searchTools, visibleTabs]);

    const tabItems: TabsProps['items'] = useMemo(
        () =>
            tabConfigs
                .filter(config => config.show)
                .map(config => ({
                    key: config.key,
                    label: intl.formatMessage({
                        id: config.label,
                        defaultMessage: config.defaultMessage,
                    }),
                })),
        [tabConfigs, intl],
    );

    const RenderNodeList = useCallback(() => {
        const currentConfig = tabConfigs.find(config => config.key === tabIndex);
        if (!currentConfig?.show) return null;

        return (
            <div className="overflow-y-auto">
                <DraggableList
                    list={currentConfig.getData()}
                    onDragStart={onDragStart}
                    type={currentConfig.type}
                />
            </div>
        );
    }, [tabIndex, tabConfigs, onDragStart]);

    const getAppsData = useCallback(
        async (nodeType: BlockEnum.Agent | BlockEnum.Skill | 'workflow') => {
            try {
                const resData = await getAppListByMode(
                    nodeType === BlockEnum.Agent ? 'agent' : 
                    nodeType === BlockEnum.Skill ? 'skill' : 'workflow',
                    {
                        search_type: nodeType === 'workflow' ? 2 : 1,
                        apps_name: filterData.keyword
                    }
                );
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
                }
            } catch (error) {
                console.error(`Failed to fetch ${nodeType} data:`, error);
            }
        },
        [filterData]
    );

    useEffect(() => {
        getAppsData(BlockEnum.Agent);
        getAppsData(BlockEnum.Skill);
        getAppsData('workflow');
    }, [filterData]);

    const onFilterChange = useCallback((changedValues, allValues) => {
        if ('team' in changedValues) {
            setFilterData(allValues);
        }
    }, []);

    return (
        <DraggablePanel
            dragDirection="right"
            minWidth={270}
            className="fixed left-0 top-16 bg-white shadow-md"
        >
            <div className="h-[calc(100vh-110px)] flex flex-col">
                <div className="px-4 py-3">
                    <ProForm
                        submitter={false}
                        initialValues={{ team: 1 }}
                        onValuesChange={onFilterChange}
                    >
                        {showTeamSwitch && (
                            <div className="flex gap-2 items-center text-base mb-4">
                                {intl.formatMessage({
                                    id: 'workflow.nodeList',
                                    defaultMessage: '节点列表',
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
                                                value: 0,
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
                        <div className='w-full'>
                            <TagSearch className='w-full'  showAddButton={false}></TagSearch>
                        </div>
                    </ProForm>

                    <Tabs
                        activeKey={tabIndex}
                        items={tabItems}
                        onChange={key => {
                            setTabIndex(key);
                        }}
                    />
                </div>
                <div className="flex-1 overflow-y-auto">
                    <RenderNodeList />
                </div>
            </div>
        </DraggablePanel>
    );
});
