/*
 * @LastEditors: biz
 */
import { getAgentInfo, getVectorList } from '@/api/workflow';
import { ProForm, ProFormDependency, ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useReactive, useUpdateEffect } from 'ahooks';
import _ from 'lodash';
import { memo, useRef, useState } from 'react';
import WrapperEditor from '../../components/Editor/WrapperEditor';
import {
    SwitchImportToKnowledgeBase,
    SwitchManualConfirmation,
} from '../../components/Form/Switch';
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

// const resetFormNodes = (formRef, node) => {
//     if (!formRef?.current?.getFieldsValue) return;
//     const fieldNames = Object.keys(formRef.current.getFieldsValue());
//     fieldNames
//         .filter(x => node.data[x])
//         .forEach(e => {
//             formRef.current.setFieldsValue({ [e]: node.data[e] });
//         });
// };
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

    const [inputList, setInputList] = useState([]);
    const [skillList, setSkillList] = useState([
        {
            label: intl.formatMessage({
                id: 'workflow.defautAllSkill',
                defaultMessage: '',
            }),
            value: '0',
        },
    ]);
    // const [editorLoading,setEditorLoading]=useTimeout(1000)
    const [editorLoading, setEditorLoading] = useState(false);
    const [systemEditor, setSystemEditor] = useState([]);
    const [userEditor, setUserEditor] = useState([]);
    const [editorOptions, setEditorOptions] = useState([]);
    const [datasetList, setDatasetList] = useState([]);
    const getNode = useStore(state => state.getNode);
    const datasetData = useStore(state => state.datasetData);
    const edges = useStore(state => state.edges);

    // Check if current node is connected to executor_list
    const isConnectedToExecutorList = edges.some(
        edge => edge.source === node.id && edge.targetHandle === 'executor_list',
    );

    useMount(() => {
        setEditorLoading(true);
        agentInfo();

        const reset = resetFormNodes(formRef, node);
        setTimeout(() => {
            reset();
        }, 200);
        if (node?.data['prompt']?.value) {
            resetNodeInfo();
        }
        if (node.data['systemEditor']) {
            setSystemEditor(node.data['systemEditor']);
        }
        if (node.data['userEditor']) {
            setUserEditor(node.data['userEditor']);
        }
        const vars = getVariables(node.id);
        console.log(vars);

        setEditorOptions(vars);
        getDatasetList();
        setTimeout(() => {
            setEditorLoading(false);
        }, 500);
    });

    const getDatasetList = async () => {
        const res = await getVectorList();
        if (res.code == 0 && res.data?.data?.length) {
            setDatasetList(
                res.data.data.map(item => {
                    return {
                        label: item.name,
                        value: item.dataset_id,
                    };
                }),
            );
        }
    };

    const agentInfo = async () => {
        if (!node.data['baseData']?.app_id) return;
        let res;
        if (node?.data['infoData']) {
            res = {
                code: 0,
                data: node?.data['infoData'],
            };
        } else {
            res = await getAgentInfo(node.data['baseData']?.app_id);
        }

        if (res.code == 0) {
            // updateNodeData(node.id, {
            //     infoData: res.data,
            // });

            if (node?.data?.['isChild']) {
                const parentNode = getNode(node?.id);
                const executor_list = _.cloneDeep(parentNode?.data?.executor_list);
                const editIndex = executor_list?.findIndex?.(x => x.currentId == node?.currentId);
                if (executor_list?.[editIndex]?.data) {
                    executor_list[editIndex].data = Object.assign(
                        executor_list[editIndex].data || {},
                        {
                            infoData: res.data,
                        },
                    );

                    updateNodeData(parentNode?.id, {
                        executor_list: executor_list,
                    });
                }
            } else {
                updateNodeData(node.id, {
                    infoData: res.data,
                });
            }
            if (res.data?.agent?.input_variables?.properties) {
                setInputList(Object.values(res.data?.agent?.input_variables?.properties));
            }
            if (res.data?.agent_abilities_list?.length) {
                setSkillList([
                    {
                        label: intl.formatMessage({
                            id: 'workflow.defautAllSkill',
                            defaultMessage: '',
                        }),
                        value: '0',
                    },
                    ...res.data?.agent_abilities_list
                        ?.map(item => {
                            return {
                                ...item,
                                label: item.name,
                                value: item.agent_ability_id,
                            };
                        })
                        .filter(x => x.status == 1),
                ]);
            }
        }
    };

    useUpdateEffect(() => {
        setUpdateEditor(() => updateEditor + 1);
        resetNodeInfo();
    }, [node.id]);

    const resetNodeInfo = () => {
        console.log(node.data['prompt']?.value);

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
                // free: createPrompt(promptObj),
                value: JSON.stringify(promptObj),
            },
        });
    };

    const editorTableChange = (key, value) => {
        if (editorLoading) {
            return;
        }

        if (node?.data?.['isChild']) {
            const parentNode = getNode(node?.id);
            console.log(node?.id, getNode(node?.id));
            const executor_list = _.cloneDeep(parentNode?.data?.executor_list);
            const editIndex = executor_list?.findIndex(x => x.currentId == node?.currentId);
            if (!executor_list[editIndex].data) return;
            executor_list[editIndex].data = Object.assign(executor_list[editIndex].data || {}, {
                [key]: value,
            });

            updateNodeData(parentNode?.id, {
                executor_list: executor_list,
            });
        } else {
            updateNodeData(node.id, { [key]: value });
        }
    };
    const setNodeChange = (addItem: { [key: string]: any }, all) => {
        updateNodeData(node.id, all);
        if (node?.data?.['isChild']) {
            const parentNode = getNode(node?.id);
            const executor_list = _.cloneDeep(parentNode?.data?.executor_list);
            const editIndex = executor_list?.findIndex(x => x.currentId == node?.currentId);
            if (!executor_list[editIndex].data) return;
            executor_list[editIndex].data = Object.assign(executor_list[editIndex].data || {}, all);

            updateNodeData(parentNode?.id, {
                executor_list: executor_list,
            });
        } else {
            updateNodeData(node.id, all);
        }
    };

    return (
        <>
            <div className="pt-4">
                <ProForm
                    submitter={{
                        render: () => null,
                    }}
                    omitNil={false}
                    formRef={formRef}
                    layout="horizontal"
                    initialValues={{
                        ability_id: '0',
                    }}
                    autoFocusFirstInput={false}
                    onValuesChange={setNodeChange}
                >
                    {inputList.map((item, index) => {
                        return (
                            <SelectVariable
                                key={index}
                                name={`variable.${item.name}`}
                                label={item.name}
                                showSearch
                                allowClear={false}
                                node={node}
                                options={editorOptions}
                            ></SelectVariable>
                        );
                    })}

                    <ProFormSelect
                        allowClear={false}
                        options={skillList?.length ? skillList : []}
                        name="ability_id"
                        label={intl.formatMessage({
                            id: 'workflow.agentSkill',
                            defaultMessage: 'Agent',
                        })}
                    ></ProFormSelect>
                    <div className="user-form">
                        {/* <ProFormSwitch
                            name="wait_for_all_predecessors"
                            label=""
                        ></ProFormSwitch> */}
                        {/* <ProFormSwitch name="requires_upload" label=""></ProFormSwitch> */}
                        {/* <ProFormSwitch name="task_splitting" label=""></ProFormSwitch> */}
                        {/* <ProFormSwitch name="manual_confirmation" label=""></ProFormSwitch> */}
                        <SwitchManualConfirmation></SwitchManualConfirmation>
                        {!node?.data?.['isChild'] && !isConnectedToExecutorList && (
                            <SwitchImportToKnowledgeBase></SwitchImportToKnowledgeBase>
                        )}
                    </div>
                    <ProFormDependency name={['import_to_knowledge_base']}>
                        {({ import_to_knowledge_base }) => {
                            return (
                                import_to_knowledge_base && (
                                    <div>
                                        <div className="text-sm font-bold pb-2">input</div>
                                        {inputList.map((item, index) => {
                                            return (
                                                <ProFormSelect
                                                    key={index}
                                                    placeholder={intl.formatMessage({
                                                        id: 'workflow.select_to_knowledge_base',
                                                        defaultMessage: '',
                                                    })}
                                                    name={`import_to_knowledge_base.${item.name}`}
                                                    label={item.name}
                                                    options={datasetList}
                                                ></ProFormSelect>
                                            );
                                        })}
                                        <div className="text-sm font-bold pb-2">output</div>
                                        <ProFormSelect
                                            placeholder={intl.formatMessage({
                                                id: 'workflow.select_to_knowledge_base',
                                                defaultMessage: '',
                                            })}
                                            name={`import_to_knowledge_base.output.text`}
                                            label={`text`}
                                            options={datasetData?.list || []}
                                        ></ProFormSelect>
                                    </div>
                                )
                            );
                        }}
                    </ProFormDependency>
                </ProForm>
                {/* <WrapperEditor
                    placeholder="，@"
                    title="System"
                    key={node.id}
                    value={systemEditor}
                    options={editorOptions}
                    onChange={(value) => editorTableChange('systemEditor', value)}
                ></WrapperEditor> */}
                <WrapperEditor
                    placeholder={intl.formatMessage({
                        id: 'workflow.editorPles',
                        defaultMessage: '，@',
                    })}
                    title="Prompt"
                    value={userEditor}
                    options={editorOptions}
                    variables={inputList}
                    onChange={value => editorTableChange('userEditor', value)}
                ></WrapperEditor>
                {/* <SlateEditor
                    key={1}
                    id={1}
                    title="System"
                    updateEditor={updateEditor}
                    value={promptObj.system.value}
                    onChange={(value) => editorChange(value, 'system')}
                ></SlateEditor> */}
                {/* <SlateEditor
                    key={2}
                    id={2}
                    title="User"
                    updateEditor={updateEditor}
                    value={promptObj.user.value}
                    onChange={(value) => editorChange(value, 'user')}
                ></SlateEditor> */}
            </div>
        </>
    );
});
