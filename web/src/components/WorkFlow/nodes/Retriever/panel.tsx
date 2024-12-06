/*
 * @LastEditors: biz
 */
import { ProForm, ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useUpdateEffect } from 'ahooks';
import { memo, useRef } from 'react';
import useStore from '../../store';
import { AppNode } from '../../types';
import { resetFormNodes } from '../../utils/resetFormNodes';

type PromptItem = {
    serializedContent: string;
    value: object;
};
interface Prompt {
    system: PromptItem;
    user: PromptItem;
    assistant: PromptItem;
}

const transformSelectOptions = options => {
    return options.map(group => {
        return {
            label: <span>{group.label}</span>,
            title: group.value,
            options:
                group.options?.map(item => ({
                    label: <span>{item.label}</span>,
                    value: item.value,
                })) || [],
        };
    });
};

export default memo(({ node }: { node: AppNode }) => {
    const formRef = useRef(null);
    const intl = useIntl();
    const getVariables = useStore(state => state.getOutputVariables);
    const datasetData = useStore(state => state.teamDatasetData);
    const updateNodeData = useStore(state => state.updateNodeData);
    useMount(() => {
        // const fieldNames = Object.keys(formRef.current.getFieldsValue());
        // fieldNames.forEach(e => {
        //     formRef.current.setFieldsValue({ [e]: node.data[e] });
        // });
        const reset = resetFormNodes(formRef, node);
        setTimeout(() => {
            reset();
        }, 200);
    });

    useUpdateEffect(() => {}, [node.id]);

    const setNodeChange = (addItem: { [key: string]: any }) => {
        updateNodeData(node.id, addItem);
    };
    //
    return (
        <>
            <div className="pt-4">
                <ProForm
                    submitter={{
                        render: () => null,
                    }}
                    formRef={formRef}
                    omitNil={false}
                    autoFocusFirstInput={false}
                    onValuesChange={setNodeChange}
                >
                    <ProFormSelect
                        name="variable"
                        label={intl.formatMessage({
                            id: 'workflow.label.selectVariable',
                            defaultMessage: '',
                        })}
                        showSearch
                        allowClear={false}
                        request={async () => getVariables(node.id)}
                    ></ProFormSelect>
                    <ProFormSelect
                        name="datasets"
                        label={intl.formatMessage({
                            id: 'workflow.select_to_knowledge_base',
                            defaultMessage: '',
                        })}
                        showSearch
                        mode="multiple"
                        allowClear={false}
                        request={async () => datasetData?.list || []}
                    ></ProFormSelect>
                    <div className="user-form">
                        {/* <ProFormSwitch label={intl.formatMessage({ id: 'workflow.label.manualConfirmation', defaultMessage: '' })} name="manual_confirmation"></ProFormSwitch> */}
                    </div>
                </ProForm>
            </div>
        </>
    );
});
