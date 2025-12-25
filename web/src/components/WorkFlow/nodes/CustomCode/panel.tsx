/*
 * @LastEditors: biz
 */
import { DeleteOutlined } from '@ant-design/icons';
import { ProForm, ProFormList, ProFormSelect, ProFormText } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useReactive, useUpdateEffect } from 'ahooks';
import { Button, Modal, message } from 'antd';
import { memo, useEffect, useRef, useState, useCallback } from 'react';
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
import useSocketStore from '@/store/websocket';
import {
    skillDirectCorrection,
    SkillDirectCorrectionParams,
} from '@/api/workflow';
import SkillOptimizeModal from '@/pages/Creation/components/SkillOptimizeModal';
import SkillOptimizeDiffModal, {
    SkillOptimizeData,
    SkillVariableComparison,
    SkillVariableInfo,
} from '@/pages/Creation/components/SkillOptimizeDiffModal';

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
    const updateSelectedNodeData = useStore(state => state.updateSelectedNodeData);
    const getAllConnectedElements = useStore(state => state.getAllConnectedElements);
    const setDrawerOptimizeDisabled = useStore(state => state.setDrawerOptimizeDisabled);
    const setCustomCodeOptimizeHandler = useStore(state => state.setCustomCodeOptimizeHandler);
    const skillCorrectMessages = useSocketStore(state =>
        state.getTypedMessages('generate_skill_correct'),
    );

    const [optimizeModalVisible, setOptimizeModalVisible] = useState(false);
    const [optimizePrompt, setOptimizePrompt] = useState('');
    const [diffVisible, setDiffVisible] = useState(false);
    const [optimizeLoading, setOptimizeLoading] = useState(false);
    const [optimizeJob, setOptimizeJob] = useState<{ app_run_id: number; record_id: number } | null>(
        null,
    );
    const [diffBaseData, setDiffBaseData] = useState<SkillOptimizeData | null>(null);
    const [optimizedData, setOptimizedData] = useState<SkillOptimizeData | null>(null);
    const [pendingDiffBaseData, setPendingDiffBaseData] = useState<SkillOptimizeData | null>(null);
    const [nextOptimizeInputData, setNextOptimizeInputData] = useState<SkillOptimizeData | null>(
        null,
    );
    const [inputComparisons, setInputComparisons] = useState<SkillVariableComparison[]>([]);
    const [outputComparisons, setOutputComparisons] = useState<SkillVariableComparison[]>([]);
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

    useEffect(() => {
        setCustomCodeOptimizeHandler?.(node.id, handleOpenOptimize);
        return () => {
            setCustomCodeOptimizeHandler?.(node.id, undefined);
            setDrawerOptimizeDisabled?.(false);
        };
    }, [node.id, handleOpenOptimize, setCustomCodeOptimizeHandler, setDrawerOptimizeDisabled]);

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
    const setNodeChange = (addItem: { [key: string]: any }) => {
        updateNodeData(node.id, addItem);
    };
    const handleCodeChange = e => {
        console.log(e);
        updateNodeData(node.id, {
            code: e,
        });
    };

    const defaultCode = `def main(arg1: int) -> dict:
    return {
        "result": (arg1 + 2) * 3,
    }`;

    const normalizeVariableArray = (list?: any): SkillVariableInfo[] => {
        if (!list) return [];
        if (Array.isArray(list)) {
            return list.map(item => ({
                name: item?.name || '',
                type: item?.veriable || item?.type || 'string',
                required:
                    typeof item?.required === 'boolean' ? item.required : false,
                display_name: item?.display_name || item?.name || '',
                description: item?.description || '',
            }));
        }
        if (list?.properties) {
            return Object.values(list.properties).map((item: any) => ({
                name: item?.name || '',
                type: item?.type || 'string',
                required:
                    typeof item?.required === 'boolean' ? item.required : false,
                display_name: item?.display_name || item?.name || '',
                description: item?.description || '',
            }));
        }
        return [];
    };

    const buildVariableComparisons = (
        currentList: SkillVariableInfo[] = [],
        optimizedList: SkillVariableInfo[] = [],
    ): SkillVariableComparison[] => {
        const getKey = (item: SkillVariableInfo, index: number) =>
            item?.name && item.name.trim() ? item.name : `__index_${index}`;
        const optimizedMap = new Map<string, { item: SkillVariableInfo; index: number }>();
        optimizedList.forEach((item, index) => {
            optimizedMap.set(getKey(item, index), { item, index });
        });
        const usedKeys = new Set<string>();
        const comparisons: SkillVariableComparison[] = currentList.map((item, index) => {
            const key = getKey(item, index);
            const match = optimizedMap.get(key)?.item;
            if (match) {
                usedKeys.add(key);
            }
            return {
                name: item.name || key,
                current: item,
                optimized: match,
            };
        });

        optimizedList.forEach((item, index) => {
            const key = getKey(item, index);
            if (!usedKeys.has(key)) {
                comparisons.push({
                    name: item.name || key,
                    optimized: item,
                });
            }
        });

        return comparisons;
    };

    const extractCurrentData = (): SkillOptimizeData | null => {
        const formValues = formRef.current?.getFieldsValue?.() || {};
        const name = formValues?.title || node.data?.title || '';
        const description = formValues?.desc || node.data?.desc || '';
        const inputList = normalizeVariableArray(formValues?.input_variables || node.data?.input_variables);
        const outputList = normalizeVariableArray(
            formValues?.output_variables || node.data?.output_variables,
        );
        const dependenciesList = formValues?.code_dependencies || node.data?.code_dependencies || [];
        const codeString =
            typeof node.data?.code === 'string' && node.data.code
                ? node.data.code
                : formValues?.code || defaultCode;
        return {
            name,
            description,
            input_variables: inputList,
            dependencies: {
                python3: dependenciesList || [],
            },
            code: {
                python3: codeString,
            },
            output_type: 1,
            output_variables: outputList,
        };
    };

    const mapVariablesForApi = (list: SkillVariableInfo[]) =>
        list.map(item => ({
            name: item.name,
            type: item.type,
            required: item.required ?? false,
            display_name: item.display_name || item.name,
            description: item.description || '',
        }));

    const buildPayload = (
        baseData: SkillOptimizeData,
        promptText: string,
    ): SkillDirectCorrectionParams => ({
        name: baseData.name,
        description: baseData.description,
        input_variables: mapVariablesForApi(baseData.input_variables),
        dependencies: baseData.dependencies,
        code: baseData.code,
        output_type: baseData.output_type,
        output_variables: mapVariablesForApi(baseData.output_variables),
        correction_prompt: promptText,
    });

    const resetDiffState = () => {
        setDiffVisible(false);
        setOptimizedData(null);
        setDiffBaseData(null);
        setPendingDiffBaseData(null);
        setNextOptimizeInputData(null);
        setInputComparisons([]);
        setOutputComparisons([]);
        setOptimizeJob(null);
        setOptimizeLoading(false);
    };

    const handleOpenOptimize = useCallback(() => {
        if (optimizeLoading) return;
        const currentData = extractCurrentData();
        if (!currentData) {
            message.warning(
                intl.formatMessage({ id: 'skill.optimize.error.noData' }),
            );
            return;
        }
        setNextOptimizeInputData(currentData);
        setOptimizePrompt('');
        setOptimizeModalVisible(true);
        setDrawerOptimizeDisabled?.(true);
    }, [optimizeLoading, extractCurrentData, intl, setDrawerOptimizeDisabled]);

    const handleOptimizeCancel = () => {
        if (optimizeLoading && optimizeJob) return;
        setOptimizeModalVisible(false);
        if (!optimizeLoading) {
            setNextOptimizeInputData(null);
        }
        setDrawerOptimizeDisabled?.(false);
    };

    const handleOptimizeSubmit = async () => {
        if (optimizeLoading) return;
        const promptText = optimizePrompt.trim();
        if (!promptText) {
            message.warning(
                intl.formatMessage({ id: 'skill.optimize.error.required' }),
            );
            return;
        }
        let baseData = nextOptimizeInputData;
        if (!baseData) {
            baseData = extractCurrentData();
        }
        if (!baseData) {
            message.warning(
                intl.formatMessage({ id: 'skill.optimize.error.noData' }),
            );
            return;
        }
        try {
            setOptimizeModalVisible(false);
            setOptimizePrompt('');
            setPendingDiffBaseData(baseData);
            setDiffBaseData(baseData);
            setOptimizedData(null);
            setInputComparisons([]);
            setOutputComparisons([]);
            setDiffVisible(true);
            setOptimizeLoading(true);
            setDrawerOptimizeDisabled?.(true);

            const payload = buildPayload(baseData, promptText);
            const res = await skillDirectCorrection(payload);
            if (res?.code === 0 && res?.data) {
                setOptimizeJob(res.data);
            } else {
                const errorMsg =
                    res?.detail ||
                    res?.message ||
                    intl.formatMessage({ id: 'skill.optimize.error.failed' });
                message.error(errorMsg);
                resetDiffState();
            }
        } catch (error) {
            message.error(intl.formatMessage({ id: 'skill.optimize.error.failed' }));
            resetDiffState();
        }
    };

    useUpdateEffect(() => {
        if (!optimizeJob) return;
        const messagesArray = Array.isArray(skillCorrectMessages) ? skillCorrectMessages : [];
        if (!messagesArray.length) return;
        const matched = [...messagesArray]
            .reverse()
            .find(
                item =>
                    item?.data?.app_run_id === optimizeJob.app_run_id &&
                    item?.data?.exec_data?.exec_id === optimizeJob.record_id,
            );
        if (!matched) {
            return;
        }
        if (matched?.data?.status !== 3) {
            const errorMessage =
                matched?.data?.exec_data?.error ||
                matched?.data?.error ||
                intl.formatMessage({ id: 'skill.optimize.error.failed' });
            message.error(errorMessage);
            setOptimizeLoading(false);
            setOptimizeJob(null);
            setPendingDiffBaseData(null);
            setNextOptimizeInputData(null);
            return;
        }
        const rawValue = matched?.data?.exec_data?.outputs?.value;
        try {
            let payload = rawValue;
            if (typeof payload === 'string') {
                payload = JSON.parse(payload);
            }
            if (typeof payload === 'string') {
                payload = JSON.parse(payload);
            }
            const normalized: SkillOptimizeData = {
                name: payload?.name || '',
                description: payload?.description || '',
                input_variables: normalizeVariableArray(payload?.input_variables),
                dependencies:
                    Array.isArray(payload?.dependencies) || typeof payload?.dependencies === 'string'
                        ? { python3: Array.isArray(payload?.dependencies) ? payload.dependencies : [payload.dependencies] }
                        : {
                              python3: Array.isArray(payload?.dependencies?.python3)
                                  ? payload.dependencies.python3
                                  : [],
                          },
                code: {
                    python3:
                        typeof payload?.code === 'object' && payload?.code !== null
                            ? payload.code.python3 || ''
                            : payload?.code || defaultCode,
                },
                output_type:
                    typeof payload?.output_type === 'number' && payload.output_type > 0
                        ? payload.output_type
                        : 1,
                output_variables: normalizeVariableArray(payload?.output_variables),
            };
            const effectiveBase = pendingDiffBaseData || diffBaseData || normalized;
            setDiffBaseData(effectiveBase);
            setOptimizedData(normalized);
            setInputComparisons(
                buildVariableComparisons(
                    effectiveBase?.input_variables || [],
                    normalized.input_variables || [],
                ),
            );
            setOutputComparisons(
                buildVariableComparisons(
                    effectiveBase?.output_variables || [],
                    normalized.output_variables || [],
                ),
            );
            setOptimizeLoading(false);
            setOptimizeJob(null);
            setPendingDiffBaseData(null);
            setNextOptimizeInputData(null);
            setDrawerOptimizeDisabled?.(false);
        } catch (error) {
            message.error(intl.formatMessage({ id: 'skill.optimize.error.invalid' }));
            setOptimizeLoading(false);
            setOptimizeJob(null);
            setPendingDiffBaseData(null);
            setNextOptimizeInputData(null);
            setDrawerOptimizeDisabled?.(false);
        }
    }, [skillCorrectMessages, optimizeJob, intl, pendingDiffBaseData, diffBaseData]);

    const applyOptimizedResult = () => {
        if (!optimizedData) return;
        const deps = optimizedData.dependencies?.python3 || [];
        const codeString = optimizedData.code?.python3 || '';
        const formValues = formRef.current?.getFieldsValue?.() || {};
        const currentInputs: any[] = formValues?.input_variables || node.data?.input_variables || [];
        const currentOutputs: any[] = formValues?.output_variables || node.data?.output_variables || [];

        const newInputs =
            optimizedData.input_variables?.map(item => {
                const match = currentInputs.find(v => v?.name === item.name);
                return {
                    name: item.name,
                    veriable: match?.veriable, // keep existing binding
                    type: item.type || 'string',
                    description: item.description || '',
                };
            }) || [];
        const newOutputs =
            optimizedData.output_variables?.map(item => {
                const match = currentOutputs.find(v => v?.name === item.name);
                return {
                    name: item.name,
                    veriable: item.type || match?.veriable || 'string',
                    type: item.type || 'string',
                    description: item.description || '',
                };
            }) || [];

        const newValues = {
            title: optimizedData.name,
            desc: optimizedData.description,
            input_variables: newInputs,
            output_variables: newOutputs,
            code_dependencies: deps,
            code: codeString,
        };
        updateNodeData(node.id, newValues);
        updateSelectedNodeData?.(node.id, {
            title: newValues.title,
            desc: newValues.desc,
            code: newValues.code,
            input_variables: newInputs,
            output_variables: newOutputs,
            code_dependencies: deps,
        });
        formRef.current?.setFieldsValue?.({
            title: newValues.title,
            desc: newValues.desc,
            input_variables: newInputs,
            output_variables: newOutputs,
            code_dependencies: deps,
        });
        setUpdateEditor(v => v + 1);
        message.success(intl.formatMessage({ id: 'skill.optimize.apply.success' }));
        resetDiffState();
        setDrawerOptimizeDisabled?.(false);
    };

    const handleDiffCancel = () => {
        if (!diffVisible) return;
        Modal.confirm({
            centered: true,
            title: intl.formatMessage({ id: 'skill.optimize.diff.confirm.title' }),
            content: intl.formatMessage({ id: 'skill.optimize.diff.confirm.content' }),
            okText: intl.formatMessage({ id: 'skill.optimize.diff.confirm.ok' }),
            cancelText: intl.formatMessage({ id: 'skill.optimize.diff.confirm.cancel' }),
            onOk: () => {
                resetDiffState();
                setDrawerOptimizeDisabled?.(false);
            },
        });
    };

    const handleContinueOptimize = () => {
        if (!optimizedData || optimizeLoading) return;
        const baseData = optimizedData;
        setNextOptimizeInputData(baseData);
        setOptimizePrompt('');
        setOptimizeModalVisible(true);
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
${intl.formatMessage({ id: 'customcode.notice.file.return.example' })}

${intl.formatMessage({ id: 'customcode.notice.async.wait' })}：
${intl.formatMessage({ id: 'customcode.notice.async.wait.desc' })}
${intl.formatMessage({ id: 'customcode.notice.async.wait.api' })}
${intl.formatMessage({ id: 'customcode.notice.async.wait.params' })}
${intl.formatMessage({ id: 'customcode.notice.async.wait.redis' })}
${intl.formatMessage({ id: 'customcode.notice.async.wait.example' })}`}
                    </div>
                    <div className="h-80 mb-4">
                        <CodeEditor
                            language="python3"
                            key={`code-${updateEditor}`}
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
            <SkillOptimizeModal
                open={optimizeModalVisible}
                loading={optimizeLoading}
                title={intl.formatMessage({ id: 'workflow.customcode.optimize.modal.title' })}
                description={intl.formatMessage({
                    id: 'workflow.customcode.optimize.modal.desc'
                })}
                placeholder={intl.formatMessage({ id: 'workflow.customcode.optimize.modal.placeholder' })}
                okText={intl.formatMessage({ id: 'workflow.customcode.optimize.submit' })}
                cancelText={intl.formatMessage({ id: 'workflow.customcode.optimize.cancel' })}
                value={optimizePrompt}
                onChange={setOptimizePrompt}
                onOk={handleOptimizeSubmit}
                onCancel={handleOptimizeCancel}
            />
            <SkillOptimizeDiffModal
                open={diffVisible}
                current={diffBaseData}
                optimized={optimizedData}
                loading={optimizeLoading && !optimizedData}
                inputComparisons={inputComparisons}
                outputComparisons={outputComparisons}
                nameTitleOverride={intl.formatMessage({
                    id: 'workflow.customcode.optimize.diff.name',
                    defaultMessage: 'Node Name',
                })}
                descriptionTitleOverride={intl.formatMessage({
                    id: 'workflow.customcode.optimize.diff.description',
                    defaultMessage: 'Node Description',
                })}
                showOutputType={false}
                onApply={applyOptimizedResult}
                onCancel={handleDiffCancel}
                onContinue={optimizedData ? handleContinueOptimize : undefined}
                applying={optimizeLoading}
                continuing={optimizeLoading && !!optimizeJob}
            />
        </>
    );
});
