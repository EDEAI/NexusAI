import { useCallback, useEffect } from 'react';
import { useNodeList } from './useNodeList';
import { useNodeSearch } from './useNodeSearch';
import { useNodeFilter } from './useNodeFilter';
import { useNodeTabs } from './useNodeTabs';
import {
    FilterData,
    UseNodeListOptions,
    UseNodeSearchOptions,
    UseNodeTabsOptions,
} from './types';

interface UseNodePanelOptions
    extends UseNodeListOptions,
        UseNodeSearchOptions,
        UseNodeTabsOptions {
    initialFilter?: Partial<FilterData>;
    debounceDelay?: number;
}

export const useNodePanel = (options: UseNodePanelOptions = {}) => {
    const {
        // Filter options
        initialFilter,
        debounceDelay,
        
        // List options
        cacheExpiry,
        
        // Search options
        nodeSearchThreshold,
        toolSearchThreshold,
        
        // Tabs options
        visibleTabs,
        defaultActiveTab,
    } = options;

    // Initialize individual hooks
    const nodeList = useNodeList({ cacheExpiry });
    const nodeSearch = useNodeSearch({ nodeSearchThreshold, toolSearchThreshold });
    const nodeFilter = useNodeFilter({ initialFilter, debounceDelay });

    // Initialize tabs with dependencies
    const nodeTabs = useNodeTabs(
        { visibleTabs, defaultActiveTab },
        {
            baseNodes: nodeList.baseNodes,
            searchNodeList: nodeList.searchNodeList,
            searchTools: nodeList.searchTools,
            filterData: nodeFilter.filterData,
            searchNodesByKeyword: nodeSearch.searchNodesByKeyword,
            searchToolsByKeyword: nodeSearch.searchToolsByKeyword,
            getAppsData: nodeList.getAppsData,
        },
    );

    // Clear cache when team changes
    useEffect(() => {
        nodeList.clearCache();
    }, [nodeFilter.filterData.team, nodeList.clearCache]);

    // Drag and drop handler
    const onDragStart = useCallback((event: React.DragEvent, nodeType: string, item: any) => {
        event.dataTransfer.setData(
            'application/reactflow',
            JSON.stringify({ type: nodeType, item }),
        );
        event.dataTransfer.effectAllowed = 'move';
    }, []);

    // Get data for current tab
    const getCurrentTabData = useCallback(async () => {
        const currentConfig = nodeTabs.getCurrentTabConfig();
        if (!currentConfig) return [];
        
        try {
            const data = await currentConfig.getData();
            return data?.map((item: any, index: number) => ({
                ...item,
                id: `${currentConfig.tabKey}-${index}`,
            })) || [];
        } catch (error) {
            console.error('Failed to fetch current tab data:', error);
            return [];
        }
    }, [nodeTabs]);

    // Get filtered/searched data for all tabs (for search mode)
    const getAllTabsData = useCallback(async () => {
        const results = await Promise.all(
            nodeTabs.tabConfigs.map(async (config) => {
                try {
                    const data = await config.getData();
                    const processedData = data?.map((item: any, index: number) => ({
                        ...item,
                        id: `${config.tabKey}-${index}`,
                    })) || [];
                    
                    return {
                        tabKey: config.tabKey,
                        label: config.label,
                        defaultMessage: config.defaultMessage,
                        type: config.type,
                        data: processedData,
                    };
                } catch (error) {
                    console.error(`Failed to fetch ${config.tabKey} data:`, error);
                    return {
                        tabKey: config.tabKey,
                        label: config.label,
                        defaultMessage: config.defaultMessage,
                        type: config.type,
                        data: [],
                    };
                }
            })
        );
        
        return results;
    }, [nodeTabs.tabConfigs]);

    return {
        // Filter state and actions
        filterData: nodeFilter.filterData,
        setFilterData: nodeFilter.setFilterData,
        onFilterChange: nodeFilter.onFilterChange,
        updateFilter: nodeFilter.updateFilter,
        resetFilter: nodeFilter.resetFilter,

        // Tab state and actions
        tabIndex: nodeTabs.tabIndex,
        setTabIndex: nodeTabs.setTabIndex,
        tabConfigs: nodeTabs.tabConfigs,
        tabItems: nodeTabs.tabItems,
        getCurrentTabConfig: nodeTabs.getCurrentTabConfig,

        // Node data
        baseNodes: nodeList.baseNodes,
        searchNodeList: nodeList.searchNodeList,
        searchTools: nodeList.searchTools,
        getNodesByType: nodeList.getNodesByType,

        // Search functions
        searchNodesByKeyword: nodeSearch.searchNodesByKeyword,
        searchToolsByKeyword: nodeSearch.searchToolsByKeyword,
        searchWorkflowsByKeyword: nodeSearch.searchWorkflowsByKeyword,
        lang: nodeSearch.lang,

        // Cache management
        clearCache: nodeList.clearCache,
        dataCache: nodeList.dataCache,

        // Data fetching
        getAppsData: nodeList.getAppsData,
        getCurrentTabData,
        getAllTabsData,

        // Event handlers
        onDragStart,
    };
};



