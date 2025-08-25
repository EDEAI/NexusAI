import { useCallback, useRef, useState, useEffect } from 'react';
import { useSetState } from 'ahooks';
import { getAppListByMode } from '@/api/workflow';
import { getBaseNode } from '@/components/WorkFlow/nodes/nodeDisperse';
import { BlockEnum } from '@/components/WorkFlow/types';
import useStore from '@/components/WorkFlow/store';
import { CacheData, FilterData, SearchNodeList, UseNodeListOptions } from './types';

export const useNodeList = (options: UseNodeListOptions = {}) => {
    const { cacheExpiry = 60000 } = options;

    const originNodes = getBaseNode();
    const toolData = useStore(state => state.toolData);
    
    const [searchNodeList, setSearchNodeList] = useSetState<SearchNodeList>({
        [BlockEnum.Agent]: [],
        [BlockEnum.Skill]: [],
        ['workflow']: [],
    });

    const [searchTools, setSearchTools] = useState([]);
    const dataCache = useRef<CacheData>({});

    // Get base nodes (excluding certain types)
    const baseNodes = Object.values(originNodes)
        .filter(
            item =>
                ![
                    BlockEnum.Start,
                    BlockEnum.Agent,
                    BlockEnum.Tool,
                    BlockEnum.Skill,
                ].includes(item.base.type),
        )
        .map(item => item.base);

    // Update search tools when toolData changes
    useEffect(() => {
        setSearchTools(toolData?.list || []);
    }, [toolData]);

    const getAppsData = useCallback(
        async (nodeType: BlockEnum.Agent | BlockEnum.Skill | 'workflow', filterData: FilterData) => {
            const cacheKey = `${nodeType}-${filterData.team||''}-${
                filterData.keyword||''
            }-${filterData?.tag?.join(',') || ''}`;
            const cachedItem = dataCache.current[cacheKey];

            // Check cache validity
            if (
                cachedItem &&
                Date.now() - cachedItem.timestamp < cacheExpiry &&
                JSON.stringify(cachedItem.params) === JSON.stringify(filterData)
            ) {
                console.log(`[Cache hit] Using cached data for ${nodeType}`);
                return cachedItem.data;
            }

            console.log(`[Cache miss] Fetching data for ${nodeType}`);
            try {
                const resData = await getAppListByMode(nodeType, {
                    search_type: filterData.team,
                    apps_name: filterData.keyword,
                    tag_ids: filterData.tag?.join(',') || '',
                });

                if (
                    resData?.code === 0 &&
                    resData?.data &&
                    Array.isArray((resData.data as any).list) &&
                    (resData.data as any).list.length > 0
                ) {
                    const dataList = (resData.data as any).list;
                    const list = dataList
                        .filter((item: any) => item.publish_status == 1)
                        .map((item: any) => ({
                            ...originNodes[nodeType]?.base,
                            data: {
                                ...originNodes[nodeType]?.base.data,
                                title: item.name,
                                desc: item.description,
                            },
                            baseData: item,
                        }));

                    // Cache the result
                    dataCache.current[cacheKey] = {
                        data: list,
                        timestamp: Date.now(),
                        params: { ...filterData },
                    };

                    setSearchNodeList({ [nodeType]: list });
                    return list;
                }
                return [];
            } catch (error) {
                console.error(`Failed to fetch ${nodeType} data:`, error);
                return [];
            }
        },
        [cacheExpiry, originNodes, setSearchNodeList],
    );

    const clearCache = useCallback(() => {
        dataCache.current = {};
    }, []);

    const getNodesByType = useCallback(
        (type: 'base' | 'agent' | 'skill' | 'workflow' | 'tools') => {
            switch (type) {
                case 'base':
                    return baseNodes;
                case 'agent':
                    return searchNodeList[BlockEnum.Agent] || [];
                case 'skill':
                    return searchNodeList[BlockEnum.Skill] || [];
                case 'workflow':
                    return searchNodeList['workflow'] || [];
                case 'tools':
                    return searchTools;
                default:
                    return [];
            }
        },
        [baseNodes, searchNodeList, searchTools],
    );

    return {
        baseNodes,
        searchNodeList,
        searchTools,
        getAppsData,
        getNodesByType,
        clearCache,
        dataCache: dataCache.current,
    };
};



