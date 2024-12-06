import useStore from '../store';
import { parseText } from '../transformWrokFlow';

/*
 * @LastEditors: biz
 */
const validateAndParseNodeData = (node, fieldName) => {
    try {
        const vars = parseText(node.data[fieldName]);
        if (vars?.length) {
            const getNodeVars = useStore.getState().getOutputVariables(node.id);
            const isValidVar = getNodeVars?.some(
                x => x.id === vars[0]?.identifier && x?.createVar?.name === vars[0]?.fieldName,
            );
            return isValidVar;
        }
    } catch (error) {
        console.error('Error parsing text:', error);
    }
    return true;
};

const isDatasetValid = (node, fieldName) => {
    if (!fieldName.includes('import_to_knowledge_base')||node.data[fieldName]===true) {
        return true;
    }
    const datasetList = useStore.getState()?.datasetData?.list;
    if (!datasetList) {
        return false;
    }
    return datasetList.some(x => x.dataset_id === node.data[fieldName]);
};

export const resetFormNodes = (formRef, node, more = []) => {
    const updateFields = () => {
        if (!formRef?.current?.getFieldsValue) return;
        const currentValues = formRef.current.getFieldsValue();
        const fieldNames = Object.keys(currentValues).concat(more);

        fieldNames
            .filter(x => node.data[x])
            .forEach(e => {
                if (currentValues[e] !== node.data[e]) {
                    if (!isDatasetValid(node, e)) return;
                    if (!validateAndParseNodeData(node, e)) return;
                    formRef.current.setFieldsValue({ [e]: node.data[e] });
                }
            });
    };

    formRef.current.resetFields();
    updateFields();

    return updateFields;
};
export const resetFormNodesData = (formRef, node, more = [], key = 'form') => {
    if (!formRef?.current?.getFieldsValue || !node.data?.[key]) return;
    formRef.current.resetFields();
    const fieldNames = Object.keys(formRef.current.getFieldsValue()).concat(more);

    fieldNames
        .filter(x => node.data[key][x])
        .forEach(e => {
            formRef.current.setFieldsValue({ [e]: node.data[key][e] });
        });
    return () => {
        if (!formRef?.current?.getFieldsValue) return;
        const fieldNames = Object.keys(formRef.current.getFieldsValue()).concat(more);
        fieldNames
            .filter(x => node.data[key][x])
            .forEach(e => {
                formRef.current.setFieldsValue({ [e]: node.data[key][e] });
            });
    };
};
