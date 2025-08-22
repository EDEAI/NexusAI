import { useCallback, useEffect, useState } from 'react';
import { useIntl, getLocale } from 'umi';
import { debounce } from 'lodash';
import Fuse from 'fuse.js';
import { useNodePanel } from './useNodePanel';
import useStore from '@/components/WorkFlow/store';
import { getBaseNode } from '@/components/WorkFlow/nodes/nodeDisperse';
import { BlockEnum } from '@/components/WorkFlow/types';

interface UseCreateNodesToolbarOptions {
    debounceDelay?: number;
    searchThreshold?: number;
}

export const useCreateNodesToolbar = (options: UseCreateNodesToolbarOptions = {}) => {
    const { debounceDelay = 300, searchThreshold = 0.3 } = options;
    
    const intl = useIntl();
    const lang = getLocale() === 'en-US' ? 'en_US' : 'zh_Hans';
    
    // Get data from store
    const agentData = useStore(state => state.agentData);
    const skillData = useStore(state => state.skillData);
    const toolData = useStore(state => state.toolData);
    
    // State management
    const [tabIndex, setTabIndex] = useState('1');
    const [searchNode, setSearchNode] = useState([]);
    const [toolsShow, setToolsShow] = useState(false);
    
    // Get base nodes
    const baseNodes = Object.values(getBaseNode()).filter(
        item => ![BlockEnum.Start, BlockEnum.Agent, BlockEnum.Tool, BlockEnum.Skill].includes(item.icon),
    );
    
    // Prepare lists
    const agentList = [...(agentData?.team?.list || []), ...(agentData?.user?.list || [])];
    const skillList = [...(skillData?.user?.list || []), ...(skillData?.team?.list || [])];
    
    // Transform data function - keep original logic
    const transformData = useCallback(
        (tabKey: string) => {
            let setData = null;
            
            if (tabKey === '1') {
                setData = baseNodes;
            } else if (tabKey === '2') {
                setData = agentList.map(item => ({
                    ...item,
                    title: item.name,
                })) || [];
            } else if (tabKey === '3') {
                setData = [];
                
                if (toolData?.list && Array.isArray(toolData.list)) {
                    toolData.list.forEach((category, categoryIndex) => {
                        if (category && category.tools && Array.isArray(category.tools)) {
                            category.tools.forEach((tool, toolIndex) => {
                                if (tool && tool.identity) {
                                    setData.push({
                                        ...tool,
                                        title:
                                            tool?.identity?.label?.[lang] ||
                                            tool?.identity?.label?.['en_US'] ||
                                            intl.formatMessage({
                                                id: 'workflow.tool',
                                                defaultMessage: 'Tool',
                                            }),
                                        categoryName: 
                                            category?.identity?.label?.[lang] || 
                                            category?.identity?.label?.['en_US'] || 
                                            'Unknown Category',
                                        categoryIcon: category?.identity?.icon,
                                        authorization_status: category.authorization_status,
                                        groupName: category?.identity?.name,
                                        credentials_for_provider: category?.credentials_for_provider,
                                        categoryIndex,
                                        toolIndex,
                                    });
                                }
                            });
                        }
                    });
                }
            } else if (tabKey === '4') {
                setData = skillList?.map(item => ({
                    ...item,
                    title: item.name,
                })) || [];
            }
            
            return setData || [];
        },
        [baseNodes, agentList, toolData, skillList, lang, intl],
    );
    
    // Search function - keep original search logic
    const performSearch = useCallback(
        (keyword: string, currentTabIndex: string) => {
            let searchFrom = transformData(currentTabIndex);

            if (!keyword) {
                setSearchNode(searchFrom);
                return;
            }

            let searchKeys: string[] = [];
            if (currentTabIndex === '1') {
                searchKeys = ['title', 'type', 'data.desc', 'data.title'];
            } else if (currentTabIndex === '2') {
                searchKeys = ['title', 'name', 'description'];
            } else if (currentTabIndex === '3') {
                searchKeys = [
                    'title',
                    'categoryName',
                    'description.human.zh_Hans',
                    'description.human.en_US',
                ];
            } else if (currentTabIndex === '4') {
                searchKeys = ['title', 'name', 'description'];
            }

            const fuse = new Fuse(searchFrom, {
                keys: searchKeys,
                threshold: searchThreshold,
                includeScore: true,
            });

            const results = fuse.search(keyword);
            const searchResults = results.map(result => result.item);
            setSearchNode(searchResults);
        },
        [transformData, searchThreshold],
    );

    const debouncedSearch = useCallback(
        debounce((keyword: string, currentTabIndex: string) => {
            performSearch(keyword, currentTabIndex);
        }, debounceDelay),
        [performSearch, debounceDelay],
    );

    // Tab change handler
    const onTabChange = useCallback((newTabIndex: string) => {
        setTabIndex(newTabIndex);
        setSearchNode(transformData(newTabIndex));
    }, [transformData]);

    // Search handler
    const handleSearch = useCallback((keyword: string) => {
        debouncedSearch(keyword, tabIndex);
    }, [debouncedSearch, tabIndex]);

    // Initialize data when component mounts
    useEffect(() => {
        setSearchNode(transformData('1'));
    }, [transformData]);

    // Update data when tab changes
    useEffect(() => {
        if (!toolsShow) {
            setTabIndex('1');
            setSearchNode(baseNodes);
        }
    }, [toolsShow, baseNodes]);

    // Update tool data when it changes
    useEffect(() => {
        if (tabIndex === '3' && toolData?.list) {
            const newData = transformData('3');
            setSearchNode(newData);
        }
    }, [toolData, tabIndex, transformData]);

    // Cleanup debounced search on unmount
    useEffect(() => {
        return () => {
            debouncedSearch.cancel();
        };
    }, [debouncedSearch]);

    // Group tools for display - keep original grouping logic
    const getGroupedTools = useCallback(() => {
        if (tabIndex !== '3' || !searchNode || !Array.isArray(searchNode) || searchNode.length === 0) {
            return null;
        }

        return searchNode.reduce((groups: any, tool: any) => {
            if (!tool || !tool.title) {
                return groups;
            }
            
            const categoryName = tool.categoryName || 'Unknown';
            if (!groups[categoryName]) {
                groups[categoryName] = {
                    categoryName,
                    categoryIcon: tool.categoryIcon,
                    tools: [],
                };
            }
            groups[categoryName].tools.push(tool);
            return groups;
        }, {});
    }, [tabIndex, searchNode]);

    // Tab items configuration
    const tabItems = [
        {
            key: '1',
            label: intl.formatMessage({ id: 'workflow.node', defaultMessage: 'Node' }),
        },
        {
            key: '2',
            label: intl.formatMessage({ id: 'workflow.agent', defaultMessage: 'Agent' }),
        },
        {
            key: '3',
            label: intl.formatMessage({ id: 'workflow.tool', defaultMessage: 'Tool' }),
        },
        {
            key: '4',
            label: intl.formatMessage({ id: 'workflow.skill', defaultMessage: 'Skill' }),
        },
    ];

    return {
        // State
        tabIndex,
        searchNode,
        toolsShow,
        setToolsShow,
        
        // Data
        baseNodes,
        agentList,
        skillList,
        toolData,
        tabItems,
        
        // Computed
        groupedTools: getGroupedTools(),
        
        // Methods
        onTabChange,
        handleSearch,
        transformData,
        performSearch,
        
        // Utils
        lang,
        intl,
    };
};



