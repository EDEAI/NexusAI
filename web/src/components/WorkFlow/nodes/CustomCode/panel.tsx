/*
 * @LastEditors: biz
 */
import { DeleteOutlined } from '@ant-design/icons';
import { ProForm, ProFormList, ProFormSelect, ProFormText } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useReactive, useUpdateEffect } from 'ahooks';
import { Button } from 'antd';
import { memo, useRef, useState } from 'react';
import CodeEditor from '../../components/Editor/CodeEditor';
import { SelectVariable } from '../../components/Form/Select';
import {
    SwitchManualConfirmation,
    SwitchWaitForAllPredecessors,
} from '../../components/Form/Switch';
import useVariables from '../../hooks/useVariables';
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

export default memo(({ node }: { node: AppNode }) => {
    const intl = useIntl();
    const promptObj = useReactive<Prompt>({
        system: { serializedContent: '', value: {} },
        user: { serializedContent: '', value: {} },
        assistant: { serializedContent: '', value: {} },
    });

    const formRef = useRef(null);
    const [updateEditor, setUpdateEditor] = useState(0);
    const getVariables = useVariables();
    const updateNodeData = useStore(state => state.updateNodeData);
    const getAllConnectedElements = useStore(state => state.getAllConnectedElements);
    useMount(() => {
        // const fieldNames = Object.keys(formRef.current.getFieldsValue());
        // fieldNames.forEach((e) => {
        //     formRef.current.setFieldsValue({ [e]: node.data[e] });
        // });
        resetFormNodes(formRef, node);
        if (node?.data['prompt']?.value) {
            resetNodeInfo();
        }
        const prevNode = getAllConnectedElements(node.id, 'target');
        console.log(prevNode);
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
    const setNodeChange = (addItem: { [key: string]: any }, allValues) => {
        updateNodeData(node.id, allValues);
    };
    const handleCodeChange = e => {
        console.log(e);
        updateNodeData(node.id, {
            code: e,
        });
    };
    return (
        <>
            <div className="pt-4">
                <ProForm
                    submitter={{
                        render: () => null,
                    }}
                    autoFocusFirstInput={false}
                    omitNil={false}
                    initialValues={{
                        input_variables: [
                            {
                                name: 'arg1',
                            },
                        ],
                        output_variables: [
                            {
                                name: 'result',
                                veriable: 'number',
                            },
                        ],
                    }}
                    formRef={formRef}
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
                                    colSize={12}
                                    name="veriable"
                                    filterFn={()=>true}
                                    node={node}
                                ></SelectVariable>
                            </div>
                        </div>
                    </ProFormList>

                    <ProFormSelect
                        label={intl.formatMessage({
                            id: 'workflow.label.dependencies',
                            defaultMessage: '',
                        })}
                        mode="tags"
                        name="code_dependencies"
                        placeholder={intl.formatMessage({
                            id: 'workflow.placeholder.enterDependencies',
                            defaultMessage: '，,',
                        })}
                        allowClear
                        tooltip={intl.formatMessage({
                            id: 'workflow.tooltip.dependencies',
                            defaultMessage: 'python，pip',
                        })}
                        fieldProps={{
                            open: false,
                            tokenSeparators: [',', ' '],
                        }}
                    ></ProFormSelect>
                    <div className="text-xs text-gray-500 p-3 whitespace-pre-line border-l-4 mb-2 border-gray-300 bg-gray-50">
                        {`${intl.formatMessage({ id: 'customcode.notice.title' })}:

${intl.formatMessage({ id: 'customcode.notice.file.write' })}：
${intl.formatMessage({ id: 'customcode.notice.file.write.desc' })}
${intl.formatMessage({ id: 'customcode.notice.file.write.example' })}

${intl.formatMessage({ id: 'customcode.notice.file.return' })}：
${intl.formatMessage({ id: 'customcode.notice.file.return.desc' })}
${intl.formatMessage({ id: 'customcode.notice.file.return.example' })}`}
                    </div>
                    <div className="h-80 mb-4">
                        <CodeEditor
                            language="python3"
                            value={
                                node.data['code'] ||
                                `def main(arg1: int) -> dict:
    return {
        "result": (arg1 + 2) * 3,
    }`
                            }
                            onChange={handleCodeChange}
                            title={`python3`}
                        ></CodeEditor>
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
                        creatorRecord={{
                            veriable: 'string',
                        }}
                        label={intl.formatMessage({
                            id: 'workflow.label.outputVariables',
                            defaultMessage: '',
                        })}
                        containerClassName="w-full"
                        copyIconProps={false}
                        name="output_variables"
                    >
                        <div className="flex gap-2">
                            <div className="flex-1">
                                <ProFormText
                                    placeholder={intl.formatMessage({
                                        id: 'workflow.placeholder.variableName',
                                        defaultMessage: '',
                                    })}
                                    colSize={12}
                                    name="name"
                                    className="w-28"
                                />
                            </div>
                            <ProFormSelect
                                placeholder={intl.formatMessage({
                                    id: 'workflow.placeholder.selectType',
                                    defaultMessage: '',
                                })}
                                colSize={12}
                                options={[
                                    {
                                        label: 'String',
                                        value: 'string',
                                    },
                                    {
                                        label: 'Number',
                                        value: 'number',
                                    },
                                    {
                                        label: 'Object',
                                        value: 'json',
                                    },
                                    {
                                        label: 'File',
                                        value: 'file',
                                    },
                                ]}
                                allowClear={false}
                                name="veriable"
                            ></ProFormSelect>
                        </div>
                    </ProFormList>
                    <div className="user-form row">
                        <SwitchWaitForAllPredecessors></SwitchWaitForAllPredecessors>
                        <SwitchManualConfirmation></SwitchManualConfirmation>
                    </div>
                </ProForm>
            </div>
        </>
    );
});
