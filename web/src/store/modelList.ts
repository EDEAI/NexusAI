import { create } from 'zustand';
import { useEffect, useMemo } from 'react';
import { getModelList } from '@/api/workflow';
import { useUserInfo } from '@/hooks/useUserInfo';

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
    currentTeamId: number | null;
    fetchModels: (teamId?: number | null, force?: boolean) => Promise<void>;
    reset: () => void;
}

export const useModelListStore = create<ModelListState>((set, get) => ({
    models: [],
    loading: false,
    error: null,
    initialized: false,
    currentTeamId: null,
    fetchModels: async (teamId = null, force = false) => {
        const state = get();
        const normalizedTeamId = teamId ?? null;
        const isSameTeam = state.currentTeamId === normalizedTeamId;

        if (!force && state.initialized && isSameTeam) {
            return;
        }

        set(prevState => ({
            ...prevState,
            loading: true,
            error: null,
            ...(isSameTeam ? {} : { models: [], initialized: false }),
        }));

        try {
            const res = await getModelList();

            if (res.code === 0) {
                set(prevState => ({
                    ...prevState,
                    models: Array.isArray(res.data?.data) ? res.data.data : [],
                    initialized: true,
                    currentTeamId: normalizedTeamId,
                    loading: false,
                }));
            } else {
                throw new Error(res.message || 'Failed to fetch models');
            }
        } catch (error) {
            set(prevState => ({
                ...prevState,
                error: error instanceof Error ? error.message : String(error),
                loading: false,
                initialized: false,
            }));
        }
    },
    reset: () => {
        set({
            models: [],
            loading: false,
            error: null,
            initialized: false,
            currentTeamId: null,
        });
    },
}));

export const useModelSelect = () => {
    const models = useModelListStore(state => state.models);
    const loading = useModelListStore(state => state.loading);
    const fetchModels = useModelListStore(state => state.fetchModels);
    const reset = useModelListStore(state => state.reset);

    const { userInfo } = useUserInfo();
    const teamId = userInfo?.team_id ?? null;

    useEffect(() => {
        if (teamId === null) {
            reset();
            return;
        }

        fetchModels(teamId);
    }, [teamId, fetchModels, reset]);

    const select = useMemo(() => {
        const safeModels = Array.isArray(models) ? models : [];

        const options = safeModels.map(supplier => ({
            label: supplier.supplier_name,
            options: Array.isArray(supplier.model_list) ? supplier.model_list.map(model => ({
                label: model.model_name,
                value: model.model_config_id,
                ...model
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
