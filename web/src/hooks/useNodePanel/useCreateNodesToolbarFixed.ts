import { useCallback, useEffect, useState } from 'react';
import { useIntl, getLocale } from 'umi';
import { debounce } from 'lodash';
import Fuse from 'fuse.js';
import useStore from '@/components/WorkFlow/store';
import { getBaseNode } from '@/components/WorkFlow/nodes/nodeDisperse';
import { BlockEnum } from '@/components/WorkFlow/types';

interface UseCreateNodesToolbarFixedOptions {
    debounceDelay?: number;
    searchThreshold?: number;
}

export const useCreateNodesToolbarFixed = (options: UseCreateNodesToolbarFixedOptions = {}) => {
    const { debounceDelay = 300, searchThreshold = 0.4 } = options;
    
    const intl = useIntl();
    const lang = getLocale() === 'en-US' ? 'en_US' : 'zh_Hans';
    
    // Get data from store
    const agentData = useStore(state => state.agentData);
    const skillData = useStore(state => state.skillData);
    const toolData = useStore(state => state.toolData);
    
    // State management - improved state management
    const [tabIndex, setTabIndex] = useState('1');
    const [currentKeyword, setCurrentKeyword] = useState(''); // Track current search keyword
    const [searchNode, setSearchNode] = useState([]);
    const [toolsShow, setToolsShow] = useState(false);
    const [isSearching, setIsSearching] = useState(false); // Searching state
    
    // Get base nodes
    const baseNodes = Object.values(getBaseNode()).filter(
        item => ![BlockEnum.Start, BlockEnum.Agent, BlockEnum.Tool, BlockEnum.Skill].includes(item.icon),
    );
    
    // Prepare lists
    const agentList = [...(agentData?.team?.list || []), ...(agentData?.user?.list || [])];
    const skillList = [...(skillData?.user?.list || []), ...(skillData?.team?.list || [])];
    
    // Improved data transformation - ensure search fields are correct
    const transformData = useCallback(
        (tabKey: string) => {
            let setData = null;
            
            if (tabKey === '1') {
                setData = baseNodes;
            } else if (tabKey === '2') {
                setData = agentList.map(item => ({
                    ...item,
                    title: item.name,
                    searchableText: `${item.name} ${item.description || ''}`, // Merge searchable text
                })) || [];
            } else if (tabKey === '3') {
                setData = [];
                
                if (toolData?.list && Array.isArray(toolData.list)) {
                    toolData.list.forEach((category, categoryIndex) => {
                        if (category && category.tools && Array.isArray(category.tools)) {
                            category.tools.forEach((tool, toolIndex) => {
                                if (tool && tool.identity) {
                                    const toolTitle = tool?.identity?.label?.[lang] ||
                                        tool?.identity?.label?.['en_US'] ||
                                        intl.formatMessage({ id: 'workflow.tool', defaultMessage: 'Tool' });
                                    
                                    const categoryName = category?.identity?.label?.[lang] || 
                                        category?.identity?.label?.['en_US'] || 
                                        'Unknown Category';
                                    
                                    const toolDesc = tool?.description?.human?.[lang] || 
                                        tool?.description?.human?.['en_US'] || 
                                        tool?.description?.llm || '';
                                    
                                    setData.push({
                                        ...tool,
                                        title: toolTitle,
                                        categoryName,
                                        categoryIcon: category?.identity?.icon,
                                        authorization_status: category.authorization_status,
                                        groupName: category?.identity?.name,
                                        credentials_for_provider: category?.credentials_for_provider,
                                        categoryIndex,
                                        toolIndex,
                                        // Preprocessed searchable text to ensure search path is correct
                                        searchableText: `${toolTitle} ${categoryName} ${toolDesc}`,
                                        toolDescription: toolDesc, // Store description separately
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
                    searchableText: `${item.name} ${item.description || ''}`, // Merge searchable text
                })) || [];
            }
            
            return setData || [];
        },
        [baseNodes, agentList, toolData, skillList, lang, intl],
    );
    
    // Improved search function - more precise search configuration
    const performSearch = useCallback(
        (keyword: string, currentTabIndex: string) => {
            const originalData = transformData(currentTabIndex);

            if (!keyword) {
                setSearchNode(originalData);
                setIsSearching(false);
                return;
            }

            setIsSearching(true);

            // Improved search keys configuration
            let searchKeys: string[] = [];
            let threshold = searchThreshold;
            
            if (currentTabIndex === '1') {
                // Base node search
                searchKeys = ['title', 'type', 'data.desc', 'data.title'];
                threshold = 0.3;
            } else if (currentTabIndex === '2') {
                // Agent search
                searchKeys = ['title', 'name', 'description', 'searchableText'];
                threshold = 0.4;
            } else if (currentTabIndex === '3') {
                // Tool search - use preprocessed fields
                searchKeys = [
                    'title',
                    'categoryName', 
                    'toolDescription',
                    'searchableText', // 使用预处理的搜索文本
                ];
                threshold = 0.4; // Slightly looser threshold for tools
            } else if (currentTabIndex === '4') {
                // Skill search
                searchKeys = ['title', 'name', 'description', 'searchableText'];
                threshold = 0.4;
            }

            const fuse = new Fuse(originalData, {
                keys: searchKeys,
                threshold,
                includeScore: true,
                ignoreLocation: true, // Ignore token location to improve match rate
                findAllMatches: true, // Find all matches
                minMatchCharLength: 1, // Minimum match length
            });

            const results = fuse.search(keyword);
            const searchResults = results.map(result => result.item);
            
            setSearchNode(searchResults);
            setIsSearching(false);
            
            // Debug info
            console.log(`Search results [${currentTabIndex}]:`, {
                keyword,
                originalCount: originalData.length,
                resultCount: searchResults.length,
                searchKeys,
                threshold
            });
        },
        [transformData, searchThreshold],
    );

    const debouncedSearch = useCallback(
        debounce((keyword: string, currentTabIndex: string) => {
            performSearch(keyword, currentTabIndex);
        }, debounceDelay),
        [performSearch, debounceDelay],
    );

    // Improved tab switching - keep search state
    const onTabChange = useCallback((newTabIndex: string) => {
        setTabIndex(newTabIndex);
        
        // Apply search in the new tab if there is a keyword
        if (currentKeyword) {
            performSearch(currentKeyword, newTabIndex);
        } else {
            setSearchNode(transformData(newTabIndex));
        }
    }, [transformData, currentKeyword, performSearch]);

    // Improved search handling - record the keyword
    const handleSearch = useCallback((keyword: string) => {
        setCurrentKeyword(keyword);
        if (keyword) {
            debouncedSearch(keyword, tabIndex);
        } else {
            // Restore original data when clearing search
            setSearchNode(transformData(tabIndex));
            setIsSearching(false);
        }
    }, [debouncedSearch, tabIndex, transformData]);

    // Initialize data when component mounts
    useEffect(() => {
        setSearchNode(transformData('1'));
    }, [transformData]);

    // Update data when toolsShow changes
    useEffect(() => {
        if (!toolsShow) {
            setTabIndex('1');
            setCurrentKeyword(''); // Clear keyword
            setSearchNode(baseNodes);
            setIsSearching(false);
        }
    }, [toolsShow, baseNodes]);

    // Update tool data when it changes - keep search state
    useEffect(() => {
        if (tabIndex === '3' && toolData?.list) {
            if (currentKeyword) {
                // If there is a keyword, re-run search
                performSearch(currentKeyword, '3');
            } else {
                // Otherwise update original data
                const newData = transformData('3');
                setSearchNode(newData);
            }
        }
    }, [toolData, tabIndex, transformData, currentKeyword, performSearch]);

    // Cleanup debounced search on unmount
    useEffect(() => {
        return () => {
            debouncedSearch.cancel();
        };
    }, [debouncedSearch]);

    // Improved tool grouping logic
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
        currentKeyword, // 新增：当前搜索词
        isSearching,    // 新增：搜索状态
        
        // Data
        baseNodes,
        agentList,
        skillList,
        toolData,
        tabItems,
        
        // Computed
        groupedTools: getGroupedTools(),
        hasSearchResults: currentKeyword ? searchNode.length > 0 : true, // 新增：是否有搜索结果
        
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



