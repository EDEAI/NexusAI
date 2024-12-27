import { getAgentList, getSkillList, getToolsList, getVectorList } from '@/api/workflow';
import { useEffect } from 'react';
import useStore from '../store';

const useFetchData = () => {
    const setAgentData = useStore(state => state.setAgentData);
    const setSkillData = useStore(state => state.setSkillData);
    const setToolData = useStore(state => state.setToolData);
    const setDatasetData = useStore(state => state.setDatasetData);
    const setTeamDatasetData = useStore(state => state.setTeamDatasetData);
    useEffect(() => {
        getAgentList(2).then(res => {
            if (res.code === 0) {
                setAgentData({ team: res.data });
            }
        });

        getAgentList(3).then(res => {
            if (res.code === 0) {
                setAgentData({ user: res.data });
            }
        });

        getSkillList(2).then(res => {
            if (res.code === 0) {
                setSkillData({ team: res.data });
            }
        });

        getSkillList(3).then(res => {
            if (res.code === 0) {
                setSkillData({ user: res.data });
            }
        });

        getToolsList().then(res => {
            if (res.code === 0) {
                setToolData({
                    list: Object.values(res.data),
                });
            }
        });
        getVectorList().then(res => {
            if (res.code == 0) {
                setDatasetData({
                    list: res.data.data.map(x => {
                        return {
                            ...x,
                            label: x.name,
                            value: x.dataset_id,
                        };
                    }),
                });
            }
        });
        getVectorList(2).then(res => {
            if (res.code == 0) {
                setTeamDatasetData({
                    list: res.data.data.map(x => {
                        return {
                            ...x,
                            label: x.name,
                            value: x.dataset_id,
                        };
                    }),
                });
            }
        });
    }, [setAgentData, setSkillData, setToolData]);
};

export default useFetchData;
