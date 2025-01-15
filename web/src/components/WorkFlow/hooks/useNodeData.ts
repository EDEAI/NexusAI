import { useState, useCallback, useEffect } from 'react';
import { message } from 'antd';
import { useIntl } from '@umijs/max';
import { getAgentList, getSkillList } from '@/api/workflow';
import { BlockEnum } from '../types';

interface UseNodeDataProps {
    nodeType: BlockEnum.Agent | BlockEnum.Skill;
    teamStatus: number;
    originNode: any;
    enabled?: boolean; 
}

export const useNodeData = ({ nodeType, teamStatus, originNode, enabled = true }: UseNodeDataProps) => {
    const intl = useIntl();
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchData = useCallback(async () => {
        if (!enabled) return; 

        try {
            setLoading(true);
            setError(null);
            
            const api = nodeType === BlockEnum.Agent ? getAgentList : getSkillList;
            const res = await api(teamStatus);

            if (res?.code === 0 && res?.data?.list?.length) {
                const formattedList = res.data.list.map(item => ({
                    ...originNode,
                    data: {
                        ...originNode.data,
                        title: item.name,
                        desc: item.description,
                    },
                    baseData: item,
                }));
                setData(formattedList);
            } else {
                throw new Error(res?.message || 'Failed to fetch data');
            }
        } catch (err) {
            const errorMessage = intl.formatMessage({ 
                id: `error.fetch.${nodeType.toLowerCase()}`,
                defaultMessage: `Failed to fetch ${nodeType} data`
            });
            setError(errorMessage);
            message.error(errorMessage);
        } finally {
            setLoading(false);
        }
    }, [nodeType, teamStatus, originNode, intl, enabled]);

    useEffect(() => {
        if (enabled) {
            fetchData();
        } else {
            setData([]);
            setLoading(false);
            setError(null);
        }
    }, [fetchData, enabled]);

    return {
        data,
        loading,
        error,
        refresh: fetchData
    };
};

export default useNodeData;
