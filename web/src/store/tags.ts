import { create } from 'zustand';
import { getTagList } from '@/api/workflow';
import { message } from 'antd';
import { useEffect } from 'react';

export interface Tag {
    id: number | string;
    name: string;
    label: string;
    value: number | string;
}

interface TagState {
    tags: Tag[];
    loading: boolean;
    error: string | null;
    initialized: boolean;
    fetchTags: (modes?: number) => Promise<void>;
}

export const useTagStore = create<TagState>((set) => ({
    tags: [],
    loading: false,
    error: null,
    initialized: false,
    fetchTags: async (modes = 0) => {
        try {
            set({ loading: true });
            const res = await getTagList(modes);
            if (res.code === 0) {
                const formattedTags = res.data?.map(x => ({
                    ...x,
                    label: x.name,
                    value: x.id,
                }));
                set({ tags: formattedTags, initialized: true });
            } else {
                throw new Error(res.message || 'Failed to fetch tags');
            }
        } catch (error) {
            set({ error: error.message });
            message.error('Failed to fetch tags');
        } finally {
            set({ loading: false });
        }
    },
}));

export const useInitialTags = () => {
    const { initialized, fetchTags } = useTagStore();

    useEffect(() => {
        if (!initialized) {
            fetchTags();
        }
    }, [initialized, fetchTags]);
}; 