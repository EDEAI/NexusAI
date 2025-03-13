/*
 * @LastEditors: biz
 */
import { ProForm, ProFormDependency, ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useReactive, useUpdateEffect } from 'ahooks';
import _ from 'lodash';
import { memo, useRef, useState } from 'react';
import WrapperEditor from '../../components/Editor/WrapperEditor';
import { SelectModelConfigId } from '../../components/Form/Select';
import {
    SwitchImportToKnowledgeBase,
    SwitchManualConfirmation,
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
    const intl = useIntl();
    const promptObj = useReactive<Prompt>({
        system: { serializedContent: '', value: {} },
        user: { serializedContent: '', value: {} },
        assistant: { serializedContent: '', value: {} },
    });

    const formRef = useRef(null);

    const [updateEditor, setUpdateEditor] = useState(0);
    const [editorLoading, setEditorLoading] = useState(false);
    const updateNodeData = useStore(state => state.updateNodeData);
    const getVariables = useStore(state => state.getOutputVariables);
    const datasetData = useStore(state => state.datasetData);

    const edges = useStore(state => state.edges);

    const [systemEditor, setSystemEditor] = useState([]);
    const [userEditor, setUserEditor] = useState([]);

    const [editorOptions, setEditorOptions] = useState([]);
    const getNode = useStore(state => state.getNode);

    // Check if current node is connected to executor_list
    const isConnectedToExecutorList = edges.some(
        edge => edge.source === node.id && edge.targetHandle === 'executor_list',
    );

    useMount(() => {
        setEditorLoading(true);

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

        setEditorOptions(vars);

        setTimeout(() => {
            setEditorLoading(false);
        }, 500);
    });

    useUpdateEffect(() => {
        setEditorLoading(true);
        setUpdateEditor(() => updateEditor + 1);
        resetNodeInfo();
        setTimeout(() => {
            setEditorLoading(false);
        }, 500);
    }, [node?.id]);

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

    const updateNodeDataHelper = (node, data) => {
        if (node?.data?.['isChild']) {
            const parentNode = getNode(node.id);
            const executor_list = _.cloneDeep(parentNode?.data?.executor_list);
            const editIndex = executor_list?.findIndex(x => x.currentId == node?.currentId);

            if (!executor_list?.[editIndex]?.data) return;
            executor_list[editIndex].data = Object.assign(
                executor_list[editIndex].data || {},
                data,
            );

            updateNodeData(parentNode?.id, {
                executor_list: executor_list,
            });
        } else {
            updateNodeData(node.id, data);
        }
    };

    const editorTableChange = (key, value) => {
        if (editorLoading) {
            return;
        }

        updateNodeDataHelper(node, { [key]: value });
    };
    const setNodeChange = (addItem: { [key: string]: any }, all) => {
        updateNodeDataHelper(node, all);
    };
    return (
        <>
            <div className="pt-4">
                <ProForm
                    submitter={{
                        render: () => null,
                    }}
                    formRef={formRef}
                    layout="horizontal"
                    omitNil={false}
                    autoFocusFirstInput={false}
                    onValuesChange={setNodeChange}
                >
                    {/* <ProFormSelect
                        allowClear={false}
                        options={modelList}
                        name="model_config_id"
                        label={intl.formatMessage({
                            id: 'workflow.label.selectModel',
                            defaultMessage: '',
                        })}
                    ></ProFormSelect> */}
                    <SelectModelConfigId
                        form={formRef}
                        name={`model_config_id`}
                    ></SelectModelConfigId>
                    <div className="user-form">
                        <SwitchManualConfirmation></SwitchManualConfirmation>
                        {!node?.data?.['isChild'] && !isConnectedToExecutorList && (
                            <SwitchImportToKnowledgeBase></SwitchImportToKnowledgeBase>
                        )}
                    </div>
                    <ProFormDependency name={['import_to_knowledge_base']}>
                        {({ import_to_knowledge_base }) => {
                            return (
                                import_to_knowledge_base && (
                                    <ProFormSelect
                                        className="flex-1"
                                        label={intl.formatMessage({
                                            id: 'workflow.label.text',
                                            defaultMessage: 'text',
                                        })}
                                        showSearch
                                        name={`import_to_knowledge_base.output.text`}
                                        request={async () => datasetData?.list || []}
                                    ></ProFormSelect>
                                )
                            );
                        }}
                    </ProFormDependency>
                </ProForm>
                <WrapperEditor
                    placeholder={intl.formatMessage({
                        id: 'workflow.placeholder.fillPrompt',
                    })}
                    title={intl.formatMessage({
                        id: 'workflow.title.system',
                        defaultMessage: 'System',
                    })}
                    value={systemEditor}
                    options={editorOptions}
                    onChange={value => editorTableChange('systemEditor', value)}
                ></WrapperEditor>
                <WrapperEditor
                    placeholder={intl.formatMessage({
                        id: 'workflow.placeholder.fillPrompt',
                    })}
                    title={intl.formatMessage({
                        id: 'workflow.title.user',
                        defaultMessage: 'User',
                    })}
                    value={userEditor}
                    options={editorOptions}
                    onChange={value => editorTableChange('userEditor', value)}
                ></WrapperEditor>
                {/* <SlateEditor
                    key={1}
                    id={1}
                    title="System"
                    updateEditor={updateEditor}
                    value={promptObj.system.value}
                    onChange={(value) => editorChange(value, 'system')}
                ></SlateEditor>
                <SlateEditor
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
