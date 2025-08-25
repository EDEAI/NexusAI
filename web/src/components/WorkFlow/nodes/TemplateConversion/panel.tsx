/*
 * @LastEditors: biz
 */
import { DeleteOutlined } from '@ant-design/icons';
import { ProForm, ProFormList, ProFormSelect, ProFormText } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useUpdateEffect } from 'ahooks';
import { Button } from 'antd';
import { memo, useRef } from 'react';
import CodeEditor from '../../components/Editor/CodeEditor';
import { SelectVariable } from '../../components/Form/Select';
import {
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
const originalOptions = [
    {
        label: '',
        value: 'start',
        options: [
            { label: 'Jack', value: 'Jack', type: 'string' },
            { label: 'Lucy', value: 'Lucy', type: 'string' },
        ],
    },
    {
        label: 'engineer',
        value: 'engineer',
        options: [
            { label: 'Chloe', value: 'Chloe', type: 'string' },
            { label: 'Lucas', value: 'Lucas', type: 'string' },
        ],
    },
];
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

    const setNodeChange = (addItem: { [key: string]: any }, allValues) => {
        updateNodeData(node.id, allValues);
    };
    const handleCodeChange = e => {
    
        updateNodeData(node.id, {
            code: e,
        });
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
                                id: 'workflow.button.addInputVariable',
                                defaultMessage: '',
                            }),
                        }}
                        label={intl.formatMessage({
                            id: 'workflow.label.inputVariables',
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
                                    placeholder={intl.formatMessage({
                                        id: 'workflow.placeholder.selectVariable',
                                        defaultMessage: '',
                                    })}
                                    name="variable"
                                    node={node}
                                ></SelectVariable>
                            </div>
                        </div>
                    </ProFormList>

                    <div className="h-80 mb-4">
                        <CodeEditor
                            language="jinja"
                            value={node.data['code']}
                            onChange={handleCodeChange}
                            title={`jinja2`}
                        ></CodeEditor>
                    </div>

                    <div className="user-form row">
                        {/* <ProFormSwitch
                            name="wait_for_all_predecessors"
                            label={intl.formatMessage({
                                id: 'workflow.label.waitForAllPredecessors',
                                defaultMessage: '',
                            })}
                        ></ProFormSwitch> */}
                        <SwitchWaitForAllPredecessors></SwitchWaitForAllPredecessors>
                        <SwitchManualConfirmation></SwitchManualConfirmation>
                    </div>
                </ProForm>
            </div>
        </>
    );
});
