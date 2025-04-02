import {
    getAgentList,
    getModelList,
    getSkillList,
    getToolsList,
    getVectorList,
} from '@/api/workflow';
import { useEffect } from 'react';
import useStore from '../store';

const useFetchData = () => {
    const setAgentData = useStore(state => state.setAgentData);
    const setSkillData = useStore(state => state.setSkillData);
    const setToolData = useStore(state => state.setToolData);
    const setDatasetData = useStore(state => state.setDatasetData);
    const setTeamDatasetData = useStore(state => state.setTeamDatasetData);
    const setModelOptionsData = useStore(state => state.setModelOptionsData);
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
        getModelList().then(res => {
            const safeModels = Array.isArray(res?.data?.data) ? res.data.data : [];

            const options = safeModels.map(supplier => ({
                label: supplier.supplier_name,
                options: Array.isArray(supplier.model_list)
                    ? supplier.model_list.map(model => ({
                          ...model,
                          label: model.model_name,
                          value: model.model_config_id,
                      }))
                    : [],
            }));

            let defaultValue;
            for (const supplier of safeModels) {
                if (Array.isArray(supplier.model_list)) {
                    const defaultModel = supplier.model_list.find(
                        model => model.model_default_used === 1,
                    );
                    if (defaultModel) {
                        defaultValue = defaultModel.model_config_id;
                        break;
                    }
                }
            }
            setModelOptionsData({
                options,
                defaultValue,
            });
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
