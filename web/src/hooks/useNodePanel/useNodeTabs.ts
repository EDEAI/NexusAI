import { useMemo, useState } from 'react';
import { useIntl } from '@umijs/max';
import { TabsProps } from 'antd';
import { BlockEnum } from '@/components/WorkFlow/types';
import { TabConfig, UseNodeTabsOptions, FilterData } from './types';

export const useNodeTabs = (
    options: UseNodeTabsOptions,
    dependencies: {
        baseNodes: any[];
        searchNodeList: any;
        searchTools: any[];
        filterData: FilterData;
        searchNodesByKeyword: (nodes: any[], keyword: string) => any[];
        searchToolsByKeyword: (tools: any[], keyword: string) => any[];
        getAppsData: (nodeType: any, filterData: FilterData) => Promise<any[]>;
    },
) => {
    const {
        visibleTabs,
        defaultActiveTab = '1',
    } = options;

    const intl = useIntl();
    const [tabIndex, setTabIndex] = useState(defaultActiveTab);

    const {
        baseNodes,
        searchNodeList,
        searchTools,
        filterData,
        searchNodesByKeyword,
        searchToolsByKeyword,
        getAppsData,
    } = dependencies;

    const tabConfigs: TabConfig[] = useMemo(() => {
        const allTabs: TabConfig[] = [
            {
                tabKey: 'node' as const,
                label: 'workflow.node',
                defaultMessage: 'Node',
                type: 'normal' as const,
                key: '1',
                getData: () =>
                    filterData.keyword
                        ? searchNodesByKeyword(baseNodes, filterData.keyword)
                        : baseNodes,
            },
            {
                tabKey: 'agent' as const,
                label: 'workflow.agent',
                defaultMessage: 'Agent',
                type: 'normal' as const,
                key: '2',
                getData: () => getAppsData(BlockEnum.Agent, filterData),
            },
            {
                tabKey: 'tool' as const,
                label: 'workflow.tool',
                defaultMessage: 'Tool',
                type: 'tools' as const,
                key: '3',
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
                key: '4',
                getData: async () => await getAppsData(BlockEnum.Skill, filterData),
            },
            // Workflow tab is commented out in original code
            // {
            //     tabKey: 'workflow' as const,
            //     label: 'workflow.list',
            //     defaultMessage: 'Workflow',
            //     type: 'workflow' as const,
            //     key: '5',
            //     getData: async () => await getAppsData('workflow', filterData),
            // },
        ];

        const filteredTabs = visibleTabs?.length
            ? allTabs.filter(tab => visibleTabs.includes(tab.tabKey))
            : allTabs;

        return filteredTabs.map((item, index) => ({
            ...item,
            key: (index + 1).toString(),
        }));
    }, [
        baseNodes,
        searchNodeList,
        searchTools,
        visibleTabs,
        filterData,
        searchNodesByKeyword,
        searchToolsByKeyword,
        getAppsData,
    ]);

    const tabItems: TabsProps['items'] = useMemo(
        () =>
            tabConfigs.map(config => ({
                key: config.key,
                label: intl.formatMessage({
                    id: config.label,
                    defaultMessage: config.defaultMessage,
                }),
            })),
        [tabConfigs, intl],
    );

    const getCurrentTabConfig = () => {
        return tabConfigs.find(config => config.key === tabIndex);
    };

    const setActiveTab = (key: string) => {
        setTabIndex(key);
    };

    return {
        tabIndex,
        setTabIndex: setActiveTab,
        tabConfigs,
        tabItems,
        getCurrentTabConfig,
    };
};



