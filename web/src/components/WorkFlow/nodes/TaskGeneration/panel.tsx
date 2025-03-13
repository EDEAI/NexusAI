/*
 * @LastEditors: biz
 */
import Callword from '@/components/callword';
import {
    ProForm,
    ProFormDependency,
    ProFormSelect,
    ProFormTextArea,
} from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount } from 'ahooks';
import { memo, useRef } from 'react';
import { SelectModelConfigId } from '../../components/Form/Select';
import {
    SwitchImportToKnowledgeBase,
    SwitchManualConfirmation,
    SwitchWaitForAllPredecessors,
} from '../../components/Form/Switch';
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

export default memo(({ node }: { node: AppNode }) => {
    const formRef = useRef(null);
    const intl = useIntl();
    const datasetData = useStore(state => state.datasetData);
    const updateNodeData = useStore(state => state.updateNodeData);
    const getVariables = useStore(state => state.getOutputVariables);

    useMount(() => {
        const reset = resetFormNodes(formRef, node);
        setTimeout(() => {
            reset();
        }, 200);
    });

    const setNodeChange = (addItem: { [key: string]: any }, allValues) => {
        updateNodeData(node.id, allValues);
    };

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
                    layout="horizontal"
                    initialValues={
                        {
                            // category_purpose: 0,
                        }
                    }
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
                    <SelectModelConfigId form={formRef} name={`model`}></SelectModelConfigId>
                    {/* <ProFormSelect
                        name="model"
                        label={intl.formatMessage({
                            id: 'workflow.label.selectModel',
                            defaultMessage: '',
                        })}
                        showSearch
                        allowClear={false}
                        request={async () => {
                            const res = (await getModelData()) || [];
                            console.log(res);
                            return res;
                        }}
                    ></ProFormSelect> */}
                    {/* <ProFormSelect
                        name="category_purpose"
                        label={intl.formatMessage({
                            id: 'workflow.label.taskPurpose',
                            defaultMessage: '',
                        })}
                        tooltip={intl.formatMessage({
                            id: 'workflow.tooltip.taskPurpose',
                            defaultMessage: '',
                        })}
                        options={[
                            {
                                label: intl.formatMessage({
                                    id: 'workflow.option.normalTask',
                                    defaultMessage: '',
                                }),
                                value: 0,
                            },
                            {
                                label: intl.formatMessage({
                                    id: 'workflow.option.documentOutline',
                                    defaultMessage: '',
                                }),
                                value: 1,
                            },
                        ]}
                    ></ProFormSelect> */}
                    <div className="user-form">
                        <SwitchWaitForAllPredecessors></SwitchWaitForAllPredecessors>
                        <SwitchManualConfirmation></SwitchManualConfirmation>
                        <SwitchImportToKnowledgeBase></SwitchImportToKnowledgeBase>
                    </div>
                    <ProFormDependency name={['import_to_knowledge_base']}>
                        {({ import_to_knowledge_base }) => {
                            return (
                                import_to_knowledge_base && (
                                    <ProFormSelect
                                        className="flex-1"
                                        label={intl.formatMessage({
                                            id: 'workflow.label.output',
                                            defaultMessage: 'output',
                                        })}
                                        showSearch
                                        name={`import_to_knowledge_base.output.output`}
                                        request={async () => datasetData?.list || []}
                                    ></ProFormSelect>
                                )
                            );
                        }}
                    </ProFormDependency>
                    <div className="flex">
                        <div className="flex-1 pt-2 border-stone-300 border rounded-md my-2">
                            <div className="px-2 flex justify-between cursor-default">
                                <div>
                                    <div className="text-sm text-gray-500 font-bold pb-1">
                                        <Callword
                                            name={intl.formatMessage({
                                                id: 'workflow.label.instruction',
                                                defaultMessage: '',
                                            })}
                                            title={intl.formatMessage({
                                                id: 'workflow.tooltip.instruction1',
                                                defaultMessage: '，、',
                                            })}
                                        ></Callword>
                                    </div>
                                </div>
                                <div></div>
                            </div>
                            <div className="overflow-y-auto">
                                <ProFormTextArea
                                    name="prompt"
                                    fieldProps={{
                                        variant: 'borderless',
                                        placeholder: intl.formatMessage({
                                            id: 'workflow.placeholder.enterInstruction',
                                            defaultMessage: '',
                                        }),
                                        autoSize: { minRows: 1, maxRows: 40 },
                                        count: {
                                            show: ({ value, count, maxLength }) => {
                                                return (
                                                    <div className="pr-2 text-blue-400">
                                                        {count}
                                                    </div>
                                                );
                                            },
                                        },
                                    }}
                                />
                            </div>
                        </div>
                    </div>
                </ProForm>
            </div>
        </>
    );
});
