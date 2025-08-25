/*
 * @LastEditors: biz
 */
import { useCallback, useState } from 'react';
import { debounce } from 'lodash';
import { FilterData } from './types';

interface UseNodeFilterOptions {
    initialFilter?: Partial<FilterData>;
    debounceDelay?: number;
}

export const useNodeFilter = (options: UseNodeFilterOptions = {}) => {
    const {
        initialFilter = { team: 1, keyword: '', tag: [] },
        debounceDelay = 500,
    } = options;

    const [filterData, setFilterData] = useState<FilterData>({
        team: 1,
        keyword: '',
        tag: [],
        ...initialFilter,
    });

    const debouncedSetFilter = useCallback(
        debounce((values: FilterData) => {
            setFilterData(values);
        }, debounceDelay),
        [debounceDelay],
    );

    const onFilterChange = useCallback(
        (changedValues: Partial<FilterData>, allValues: FilterData) => {
            if ('team' in changedValues) {
                // Team change should be immediate
                setFilterData(allValues);
            } else if ('tag' in changedValues || 'keyword' in changedValues) {
                // Search and tag changes should be debounced
                
                debouncedSetFilter(allValues);
            }
        },
        [debouncedSetFilter],
    );

    const updateFilter = useCallback((newFilter: Partial<FilterData>) => {
        setFilterData(prev => ({ ...prev, ...newFilter }));
    }, []);

    const resetFilter = useCallback(() => {
        setFilterData({ team: 1, keyword: '', tag: [] });
    }, []);

    return {
        filterData,
        setFilterData,
        onFilterChange,
        updateFilter,
        resetFilter,
        debouncedSetFilter,
    };
};



