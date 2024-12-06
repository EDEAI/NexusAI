/*
 * @LastEditors: biz
 */
import useStore from '@/components/WorkFlow/store';
import useUserStore from '@/store/user';

export const useResetPanel = () => {
    const setSelect = useStore(state => state.setSelect);
    const setRunId = useUserStore(state => state.setRunId);
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    return () => {
        setRunId(null);
        setDealtWithData(null);
        setSelect(null);
    };
};
