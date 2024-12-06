/*
 * @LastEditors: biz
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
type FlowState = {
    [key: string]: any;
};
const useDataStore = create(
    devtools<FlowState>(
        (set, get) => ({
            tempNode:[],
            setTempNode: data => {
                set(state => ({
                    tempNode: data,
                }));
            },
            addTempNode: data => {
                set(state => ({
                    tempNode: [...state.tempNode, data],
                }));
            },
           
        }),
        { name: 'useDataStore' },
    ),
);
export default useDataStore;
