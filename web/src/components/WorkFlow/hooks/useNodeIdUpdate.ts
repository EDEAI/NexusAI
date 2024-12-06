/*
 * @LastEditors: biz
 */
import { useEffect } from 'react';
import useStore from '../store';
import { AppNode } from '../types';

const useNodeIdUpdate = (update: (nodeId: string, node: AppNode) => void) => {
    const selectedNode = useStore(state => state.selectedNode);
    const showChildNode = useStore(state => state.showChildNode);
    useEffect(() => {
        update(selectedNode?.id || '', selectedNode);
    }, [selectedNode, showChildNode]);
};
function getNestedKeys(obj, path = []) {
    let result = [];
    for (let key in obj) {
        if (typeof obj[key] === 'object' && obj[key] !== null) {
            result.push(...getNestedKeys(obj[key], path.concat(key)));
        } else {
            result.push(path.concat(key));
        }
    }
    return result;
}
export default useNodeIdUpdate;
