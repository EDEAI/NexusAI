import { useState, useCallback, useEffect } from 'react';
import { getAgentList, getSkillList, getWorkflowList } from '@/api/workflow';
import { getBaseNode } from '../nodes/nodeDisperse';
import { BlockEnum } from '../types';
import { useStore } from '@umijs/max';

export type TabType = 'node' | 'agent' | 'tool' | 'skill' | 'workflow';

interface FetchParams {
    type: TabType;
    team: number;
    keyword?: string;
}

interface UseTabDataProps {
    defaultType?: TabType;
    team?: number;
    keyword?: string;
}

export const useTabData = ({ defaultType = 'node', team = 1, keyword }: UseTabDataProps = {}) => {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<Record<TabType, any[]>>({
        node: [],
        agent: [],
        tool: [],
        skill: [],
        workflow: [],
    });
    const [currentType, setCurrentType] = useState<TabType>(defaultType);

    const fetchData = useCallback(async ({ type, team, keyword }: FetchParams) => {
        try {
            setLoading(true);
            const teamStatus = team === 1 ? 3 : 2;
            let list: any[] = [];

            switch (type) {
                case 'agent': {
                    const res = await getAgentList(teamStatus);
                    list = res?.code === 0 ? res.data.list : [];
                    break;
                }
                case 'skill': {
                    const res = await getSkillList(teamStatus);
                    list = res?.code === 0 ? res.data.list : [];
                    break;
                }
                case 'workflow': {
                    const res = await getWorkflowList(team === 1 ? 1 : 2);
                    list = res?.code === 0 ? res.data.list : [];
                    break;
                }
                case 'tool': {
                    const toolData = useStore.getState().toolData;
                    list = toolData?.list || [];
                    break;
                }
                case 'node': {
                    const originNodes = getBaseNode();
                    list = Object.values(originNodes)
                        .filter(item =>
                            ![BlockEnum.Start, BlockEnum.Agent, BlockEnum.Tool, BlockEnum.Skill].includes(
                                item.base.type,
                            ),
                        )
                        .map(item => item.base);
                    break;
                }
            }

            if (keyword) {
                list = list.filter(item => {
                    const searchText = type === 'workflow'
                        ? item.name
                        : item.data?.title || item.baseData?.name || '';
                    return searchText.toLowerCase().includes(keyword.toLowerCase());
                });
            }

            setData(prev => ({
                ...prev,
                [type]: list,
            }));
        } catch (error) {
            console.error(`Failed to fetch ${type} data:`, error);
        } finally {
            setLoading(false);
        }
    }, []);

    const refresh = useCallback(() => {
        fetchData({ type: currentType, team, keyword });
    }, [currentType, team, keyword, fetchData]);

    const changeType = useCallback((type: TabType) => {
        setCurrentType(type);
        if (!data[type].length) {
            fetchData({ type, team, keyword });
        }
    }, [data, team, keyword, fetchData]);

    useEffect(() => {
        if (!data[currentType].length) {
            fetchData({ type: currentType, team, keyword });
        }
    }, [currentType, team, keyword]);

    return {
        data,
        loading,
        currentType,
        changeType,
        refresh,
    };
}; 