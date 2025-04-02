/*
 * @LastEditors: biz
 */
import { DeleteOutlined } from '@ant-design/icons';
import { ProForm, ProFormList, ProFormText } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useReactive, useUpdateEffect } from 'ahooks';
import { Button, Tooltip } from 'antd';
import { memo, useRef, useState } from 'react';
import { SelectVariable } from '../../components/Form/Select';
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

    useMount(() => {
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
    const setNodeChange = (addItem: { [key: string]: any }, allVals) => {
        updateNodeData(node.id, allVals);
    };
    
    // 自定义过滤函数 - 示例如何自定义过滤条件
    const customFilterFn = (item: any) => {
        return item.createVar.type !== 'file';
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
                                <SelectVariable 
                                    name="variable" 
                                    node={node} 
                                    filterFn={customFilterFn}
                                />
                            </div>
                        </div>
                    </ProFormList>
                </ProForm>
            </div>
        </>
    );
});
