/*
 * @LastEditors: biz
 */
import { DeleteOutlined } from '@ant-design/icons';
import { ProForm, ProFormList, ProFormSelect, ProFormText } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useReactive, useUpdateEffect } from 'ahooks';
import { Button, Tooltip } from 'antd';
import { memo, useRef, useState } from 'react';
import useStore from '../../store';
import { AppNode } from '../../types';
import { createPrompt } from '../../utils/createNode';
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
const modelList = [
    { label: 'GPT-3', value: 'GPT-3' },
    { label: 'GPT-Neo', value: 'GPT-Neo' },
    { label: 'GPT-4', value: 'GPT-4' },
    { label: 'GPT-4-32k', value: 'GPT-4-32k' },
    { label: 'GPT-4-Turbo', value: 'GPT-4-Turbo' },
    { label: 'GPT-4-Turbo-16k', value: 'GPT-4-Turbo-16k' },
    { label: 'GPT-4-Turbo-16k-0613', value: 'GPT-4-Turbo-16k-0613' },
    { label: 'GPT-4-Turbo-0613', value: 'GPT-4-Turbo-0613' },
    { label: 'GPT-4-0613', value: 'GPT-4-0613' },
    { label: 'GPT-3-Turbo', value: 'GPT-3-Turbo' },
];
export default memo(({ node }: { node: AppNode }) => {
    const intl = useIntl();
    const promptObj = useReactive<Prompt>({
        system: { serializedContent: '', value: {} },
        user: { serializedContent: '', value: {} },
        assistant: { serializedContent: '', value: {} },
    });

    const formRef = useRef(null);
    const [updateEditor, setUpdateEditor] = useState(0);

    const updateNodeData = useStore(state => state.updateNodeData);
    const getVariables = useStore(state => state.getOutputVariables);
    // const getVariables = useVariables();
    useMount(() => {
        // const fieldNames = Object.keys(formRef.current.getFieldsValue());
        // fieldNames.forEach(e => {
        //     formRef.current.setFieldsValue({ [e]: node.data[e] });
        // });

        const reset = resetFormNodes(formRef, node);
        setTimeout(() => {
            reset();
        }, 200);
        if (node?.data['prompt']?.value) {
            resetNodeInfo();
        }
    });

    useUpdateEffect(() => {
        setUpdateEditor(() => updateEditor + 1);
        resetNodeInfo();
    }, [node.id]);

    const resetNodeInfo = () => {
        try {
            const oldValue = JSON.parse(node.data['prompt'].value);
            promptObj.system = oldValue.system;
            promptObj.user = oldValue.user;
            promptObj.assistant = oldValue.assistant;
        } catch (error) {
            promptObj.system = { serializedContent: '', value: {} };
            promptObj.user = { serializedContent: '', value: {} };
            promptObj.assistant = { serializedContent: '', value: {} };
        }
    };
    const editorChange = (e: any, type: string) => {
        promptObj[type] = e;

        updateNodeData(node.id, {
            prompt: {
                free: createPrompt(promptObj),
                value: JSON.stringify(promptObj),
            },
        });
    };
    const setNodeChange = (addItem: { [key: string]: any }, allVals) => {
        updateNodeData(node.id, allVals);
    };
    return (
        <>
            <div className="pt-4">
                <ProForm
                    submitter={{
                        render: () => null,
                    }}
                    omitNil={false}
                    autoFocusFirstInput={false}
                    formRef={formRef}
                    // layout="horizontal"
                    onValuesChange={setNodeChange}
                >
                    <div className="user-form row">
                        {/* <SwitchManualConfirmation></SwitchManualConfirmation> */}
                        {/* <ProFormSwitch
                            formItemProps={{}}
                            name="wait_for_all_predecessors"
                            label=""
                        ></ProFormSwitch> */}
                    </div>
                    <ProFormList
                        deleteIconProps={{
                            Icon: (e, m) => {
                                return (
                                    <Button
                                        className="ml-2"
                                        onClick={e.onClick}
                                        icon={<DeleteOutlined />}
                                    ></Button>
                                );
                            },
                        }}
                        creatorButtonProps={{
                            creatorButtonText: intl.formatMessage({
                                id: 'workflow.button.addOutputVariable',
                                defaultMessage: '',
                            }),
                        }}
                        label={intl.formatMessage({
                            id: 'workflow.label.outputVariables',
                            defaultMessage: '',
                        })}
                        containerClassName="w-full"
                        copyIconProps={false}
                        name="input_variables"
                    >
                        <div className="flex gap-2">
                            <ProFormText
                                placeholder={intl.formatMessage({
                                    id: 'workflow.placeholder.variableName',
                                    defaultMessage: '',
                                })}
                                colSize={12}
                                width={120}
                                name="name"
                                className="w-28"
                            />
                            <div className="flex-1">
                                <ProFormSelect
                                    placeholder={intl.formatMessage({
                                        id: 'workflow.placeholder.selectVariable',
                                        defaultMessage: '',
                                    })}
                                    fieldProps={{
                                        optionRender: e => {
                                            return (
                                                <Tooltip title={e.label}>
                                                    <div title="">{e.label}</div>
                                                </Tooltip>
                                            );
                                        },
                                    }}
                                    colSize={12}
                                    name="variable"
                                    request={async () => await getVariables(node.id)}
                                ></ProFormSelect>
                            </div>
                        </div>
                    </ProFormList>
                </ProForm>
            </div>
        </>
    );
});
