/*
 * @LastEditors: biz
 */
// @LastEditors: biz
import { Variable } from '@/py2js/variables.js';
import useStore from '../store';
import { transformer } from '../transformWrokFlow';

const useVariables = () => {
    const getAllConnectedElements = useStore(state => state.getAllConnectedElements);
    return (id: string) => {
        const { connectedNodes } = getAllConnectedElements(id, 'target');
        const variables = connectedNodes.flatMap(node => {
            const {
                id,
                type,
                data: { title, outputInfo },
            } = node;
            if (!outputInfo) {
                return [];
            }
            let createVar = null;
            if (outputInfo.base) {
                createVar = {
                    [outputInfo.key]: new Variable(outputInfo.key, 'string'),
                };
            } else {
                createVar = transformer[node.type]?.variables(node.data);
            }

            return createVar
                ? Object.values(createVar).map(varObj => ({
                      title,
                      type,
                      id,
                      createVar: varObj,
                      label: `${title}.${varObj?.name}`,
                      value: `<<${id}.outputs.${varObj?.name}>>`,
                  }))
                : [];
        });

        return variables;
    };
};

export default useVariables;
