/*
 * @LastEditors: biz
 */
import { create } from 'zustand';
import { getModelList } from '@/api/workflow';
import { message } from 'antd';
import { useEffect, useMemo } from 'react';

export interface ModelConfig {
    model_config_id: number;
    model_name: string;
    model_default_used: number;
}

export interface Supplier {
    supplier_id: number;
    supplier_name: string;
    model_list: ModelConfig[];
}

export interface SelectOption {
    label: string;
    value: string | number;
    options?: SelectOption[];
}

interface ModelListState {
    models: Supplier[];
    loading: boolean;
    error: string | null;
    initialized: boolean;
    fetchModels: () => Promise<void>;
}

export const useModelListStore = create<ModelListState>((set) => ({
    models: [],
    loading: false,
    error: null,
    initialized: false,
    fetchModels: async () => {
        try {
            set({ loading: true });
            const res = await getModelList();
            if (res.code === 0) {
                set({ models: Array.isArray(res.data.data) ? res.data.data : [], initialized: true });
            } else {
                throw new Error(res.message || 'Failed to fetch models');
            }
        } catch (error) {
            set({ error: error.message });
            message.error('Failed to fetch models');
        } finally {
            set({ loading: false });
        }
    },
}));

export const useModelSelect = () => {
    const models = useModelListStore(state => state.models);
    const loading = useModelListStore(state => state.loading);
    const initialized = useModelListStore(state => state.initialized);
    const fetchModels = useModelListStore(state => state.fetchModels);

    useEffect(() => {
        if (!initialized) {
            fetchModels();
        }
    }, [initialized, fetchModels]);

    const select = useMemo(() => {
        const safeModels = Array.isArray(models) ? models : [];
        
        const options = safeModels.map(supplier => ({
            label: supplier.supplier_name,
            options: Array.isArray(supplier.model_list) ? supplier.model_list.map(model => ({
                label: model.model_name,
                value: model.model_config_id,
            })) : []
        }));

        let defaultValue: number | undefined;
        for (const supplier of safeModels) {
            if (Array.isArray(supplier.model_list)) {
                const defaultModel = supplier.model_list.find(model => model.model_default_used === 1);
                if (defaultModel) {
                    defaultValue = defaultModel.model_config_id;
                    break;
                }
            }
        }

        return {
            options,
            defaultValue
        };
    }, [models]);

    return {
        ...select,
        loading
    };
}; 