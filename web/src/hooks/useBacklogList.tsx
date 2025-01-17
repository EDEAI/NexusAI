/*
 * @LastEditors: biz
 */
import { getBacklogsList } from '@/api/workflow';
import useUserStore from '@/store/user';
import useSocketStore from '@/store/websocket';
import { useRequest } from 'ahooks';
import { useState } from 'react';

export const useBacklogList = () => {
    const [backlogData, setBacklogData] = useState<any>(null);
    const listenBakLogs = useSocketStore(state =>
        state.filterMessages('workflow_need_human_confirm'),
    );
    const workflowProgress = useSocketStore(state => state.filterMessages('workflow_run_progress'));
    const prevConfirmDealtWith = useUserStore(state => state.prevConfirmDealtWith);
    const { loading, runAsync } = useRequest(
        async () => {
            const res = await getBacklogsList({
                current: 1,
                pageSize: 10,
            });
            return res.data;
        },
        {
            refreshDeps: [listenBakLogs.length, workflowProgress.length, prevConfirmDealtWith],
            onSuccess: result => {
                setBacklogData(result);
            },
        },
    );
    return {
        loading,
        data: backlogData,
        refresh: runAsync,
    };
};
