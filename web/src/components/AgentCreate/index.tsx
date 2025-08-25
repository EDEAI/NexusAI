import {
    agentCreate,
    agentGenerate,
    agentReGenerate,
    agentSupplement,
    batchAgentCreate,
    previewBatchAgent,
    saveAgentTemporarily,
} from '@/api/workflow';
import useUserStore, { UPDATE_NOTIFICATIONS } from '@/store/user';
import useSocketStore from '@/store/websocket';
import { PullRequestOutlined } from '@ant-design/icons';
import { useRafState } from '@reactuses/core';
import { useLatest, useUpdateEffect } from 'ahooks';
import { App, Button, Modal, Radio, message } from 'antd';
import { memo, useCallback, useRef, useState } from 'react';
import BatchCreateModal, { BatchCreateRef } from './BatchCreate';
import BeforeCreate from './BeforeCreate';
import { ResultDisplayRef } from './ResultDisplay';
import BatchCreate from './strategies/BatchCreate';
import SingleCreate from './strategies/SingleCreate';
import { AgentFormData, AgentResult } from './types';
import { useIntl } from '@umijs/max';

interface AgentResult {
    name: string;
    description: string;
    prompt: string;
    tools: string[];
}

const AgentCreate = memo(() => {
    const { agentCreateOpen, setAgentCreateOpen } = useUserStore();
    const [modelOpen, setModelOpen] = useState(false);
    const [prompt, setPrompt] = useState('');
    const [singleConPrompt,setSingleConPrompt]=useState('')
    const [loading, setLoading] = useState(false);
    const [correctVisible, setCorrectVisible] = useState(false);
    const [singleAgentResult, setSingleAgentResult] = useRafState<AgentResult | null>(null);
    const [singleAgentOutput, setSingleAgentOutput] = useState<AgentResult | null>(null);
    const [batchAgentResult, setBatchAgentResult] = useRafState<AgentResult | null>(null);
    const [batchAgentOutput, setBatchAgentOutput] = useState<AgentResult | null>(null);
    const [formData, setFormData] = useState<AgentFormData | null>(null);
    const [batchModelVisible, setBatchModelVisible] = useState(false);
    const [batchLoading, setBatchLoading] = useState(false);
    const [singleGenerateId, setSingleGenerateId] = useState(null);
    const [batchGenerateId, setBatchGenerateId] = useState(null);
    const [hasProcessed, setHasProcessed] = useState(false);
    const flowMessage = useSocketStore(state => state.flowMessage);
    const resultDisplayRef = useRef<ResultDisplayRef>(null);
    const { modal } = App.useApp();
    const batchCreateRef = useRef<BatchCreateRef>(null);
    const [createType, setCreateType] = useState<'single' | 'batch' | ''>('single');
    const [batchPrompt, setBatchPrompt] = useState('');

    const [singleAgentCreateId, setSingleAgentCreateId] = useState('');
    const lastSingleAgentCreateId = useLatest(singleAgentCreateId);
    const intl = useIntl();
    const { setUpdateNotification } = useUserStore(state => ({
        setUpdateNotification: state.setUpdateNotification
    }));
    useUpdateEffect(() => {
        if (agentCreateOpen) {
            setModelOpen(agentCreateOpen);
        }
    }, [agentCreateOpen]);

    const handleOk = async () => {
        const currentValues = resultDisplayRef.current?.getValue();
        const createParams = {
            name: currentValues?.name || '',
            description: currentValues?.description || '',
            obligations: currentValues?.obligations || '',
            abilities: currentValues?.abilities || [],
            tags: currentValues?.tags || [],
        };
        if (lastSingleAgentCreateId?.current) {
            createParams.app_id = lastSingleAgentCreateId.current;
        }

        try {
            const res = await agentCreate({
                agents: [createParams],
            });
           
            if (res.code == 0) {
                message.success(
                    lastSingleAgentCreateId?.current
                        ? intl.formatMessage({ id: 'agent.create.modify.success' })
                        : intl.formatMessage({ id: 'agent.create.success' })
                );
                const app_id = res.data?.app_ids?.[0];
                setSingleAgentCreateId(app_id);
                setUpdateNotification(UPDATE_NOTIFICATIONS.AGENT_LIST, {
                    action: 'create',
                    data: {}
                });
            }
        } finally {
        }
    };

    const closeModal = () => {
        if (singleAgentResult|| batchAgentResult) {
            Modal.confirm({
                centered:true,
                title: intl.formatMessage({ id: 'agent.modal.leave.title' }),
                content: intl.formatMessage({ id: 'agent.modal.leave.content' }),
                onOk: () => {
                    handleCancel();
                },
            });
            return;
        }
        handleCancel();
    };

    const handleCancel = () => {
        setAgentCreateOpen(false);
        setModelOpen(false);
        resetState();
    };

    const toSaveAgentTemporarily = async () => {
        try {
            const res = await saveAgentTemporarily({
                ...formData,
                app_run_id: singleGenerateId?.app_run_id || 0,
                record_id: singleGenerateId?.record_id || 0,
            });
            console.log(res);
            if (res.code == 0) {
                // setHasProcessed(false);
                setSingleGenerateId(res.data);
                return true;
            }
            return false;
        } finally {
        }
    };
    const handleSubmit = async (prompt: string) => {
        setLoading(true);
        try {
            const res = await agentGenerate(prompt);
            console.log(res);
            if (res.code == 0) {
                setHasProcessed(false);
                setSingleGenerateId(res.data);
                setSingleAgentCreateId('');
            }
        } finally {
        }
    };

    const handleBatchPreviewAgent = async (prompt: string) => {
        setLoading(true);
        try {
            const res = await previewBatchAgent(prompt, batchGenerateId?.app_run_id || 0);

            if (res.code == 0) {
                setHasProcessed(false);
                setBatchGenerateId(res.data);
            }
        } finally {
        }
    };
    const handleRegenerateAgent = async () => {
        if (!singleGenerateId?.app_run_id) return;

        try {
            const toSave = await toSaveAgentTemporarily();
            if (!toSave) {
                message.error(intl.formatMessage({ id: 'agent.save.failed' }));
                return;
            }
            setLoading(true);
            const res = await agentReGenerate(singleGenerateId?.app_run_id);

            if (res.code == 0) {
                setHasProcessed(false);
                setSingleGenerateId(res.data);
            }
        } finally {
        }
    };
    const handleCorrectAgent = async prompt => {
        if (!singleGenerateId?.app_run_id) return;
        setSingleConPrompt(prompt)
        try {
            const toSave = await toSaveAgentTemporarily();
            if (!toSave) {
                message.error(intl.formatMessage({ id: 'agent.save.failed' }));
                return;
            }
            setLoading(true);
            const res = await agentSupplement(prompt, singleGenerateId?.app_run_id);

            if (res.code == 0) {
                console.log(res);
                setHasProcessed(false);
                setSingleGenerateId(res.data);
            }
        } finally {
        }
    };

    const handleBatchGenerate = async (prompt: string, count: number,batchCount:number) => {
        setBatchLoading(true);
        const params = {
            app_run_id: batchGenerateId?.app_run_id || 0,
            loop_count: batchCount,
            loop_limit: count,
            supplement_prompt: prompt,
            loop_id: 0,
        };

        const res = await batchAgentCreate(params);
        if (res.code == 0) {
            setBatchModelVisible({
                ...params,
                ...res.data,
            });

            setTimeout(() => {
                batchCreateRef.current?.reset();
            }, 100);
        }
    };
    useUpdateEffect(() => {
        if(!modelOpen) return
        const currentMessage = flowMessage?.find(
            item =>
                item?.data?.app_run_id ==
                    (createType === 'single'
                        ? singleGenerateId?.app_run_id
                        : batchGenerateId?.app_run_id) &&
                item?.data?.exec_data?.exec_id ==
                    (createType === 'single'
                        ? singleGenerateId?.record_id
                        : batchGenerateId?.record_id),
        );
        if (currentMessage && !hasProcessed) {
            try {
                const output = JSON.parse(currentMessage?.data?.exec_data?.outputs?.value);
                if (createType === 'single') {
                    setSingleAgentOutput(output);
                    setSingleAgentResult(currentMessage?.data);
                } else {
                    setBatchAgentOutput(output);
                    setBatchAgentResult(currentMessage?.data);
                }
            } catch (e) {
                console.log(e);
            }

            setLoading(false);
            setHasProcessed(true);
        }
    }, [flowMessage, singleGenerateId, batchGenerateId]);

    const handleFormChange = (values: AgentFormData) => {
        console.log(values);

        setFormData(values);
    };

    const handleBatchCreate = async () => {
        setBatchModelVisible(null);
    };


    const resetState = () => {
        setHasProcessed(false);
        setSingleGenerateId(null);
        setBatchGenerateId(null);
        setSingleAgentResult(null);
        setSingleAgentOutput(null);
        setBatchAgentResult(null);
        setBatchAgentOutput(null);
        setBatchModelVisible(false);
        setBatchLoading(false);
        setPrompt('');
        setSingleConPrompt('')
        setBatchPrompt('')
        setLoading(false);
        setCorrectVisible(false);
        setCreateType('single');
        sessionStorage.removeItem('use-local-storage-state-count');
    };

    const SelectedType = useCallback(() => {
        if (createType === 'single') {
            return (
                <SingleCreate
                    loading={loading}
                    agentCreateResult={singleAgentResult}
                    agentCreateResultOutput={singleAgentOutput}
                    correctVisible={correctVisible}
                    prompt={prompt}
                    conPrompt={singleConPrompt}
                    resultDisplayRef={resultDisplayRef}
                    onFormChange={handleFormChange}
                    onSubmit={handleSubmit}
                    onRegenerate={handleRegenerateAgent}
                    onCorrect={handleCorrectAgent}
                    onPromptChange={setPrompt}
                    onCorrectVisibleChange={setCorrectVisible}
                    onSave={handleOk}
                />
            );
        }

        return (
            <BatchCreate
                loading={loading}
                agentCreateResult={batchAgentResult}
                agentCreateResultOutput={batchAgentOutput}
                resultDisplayRef={resultDisplayRef}
                onFormChange={handleFormChange}
                onSubmit={handleBatchGenerate}
                onPreview={handleBatchPreviewAgent}
                prompt={batchPrompt}
                onPromptChange={setBatchPrompt}
            />
        );
    }, [createType, singleAgentResult, correctVisible, loading, batchAgentResult]);

    const TogggleCreateType = useCallback(() => {
        return (
            <div className="flex w-full pr-8 cursor-pointer justify-between ml-2 gap-2 items-center">
                {intl.formatMessage({ id: 'agent.create.title' })}
                <Radio.Group
                    block
                    size="small"
                    options={[
                        {
                            label: <div className="w-[80px]">
                                {intl.formatMessage({ id: 'agent.create.single' })}
                            </div>,
                            value: 'single'
                        },
                        {
                            label: <div className="w-[80px]">
                                {intl.formatMessage({ id: 'agent.create.batch' })}
                            </div>,
                            value: 'batch'
                        },
                    ]}
                    disabled={loading}
                    defaultValue={createType}
                    onChange={e => setCreateType(e.target.value)}
                    optionType="button"
                    buttonStyle="solid"
                />
            </div>
        );
    }, [createType, loading, intl]);

    useUpdateEffect(() => {
        // setSingleAgentResult(null);
    }, [createType]);
    return (
        <>
            <Modal
                title={
                    <div className="flex items-center gap-2 w-full">
                        {createType != '' ? <TogggleCreateType /> :  intl.formatMessage({ id: 'agent.create.title' })}
                    </div>
                }
                className="xl:min-w-[1200px] lg:min-w-[1000px]"
                bodyProps={{
                    className: '!h-[600px] overflow-y-auto p-4',
                }}
                open={modelOpen}
                footer={null}
                onOk={handleOk}
                centered
                onCancel={closeModal}
            >
                <div className="flex gap-4 h-full relative">
                    {createType == '' ? (
                        <>
                            <BeforeCreate
                                type={'single'}
                                onClick={() => setCreateType('single')}
                                loading={false}
                            />
                            <BeforeCreate
                                type={'batch'}
                                onClick={() => setCreateType('batch')}
                                loading={false}
                            />
                        </>
                    ) : (
                        <SelectedType />
                    )}
                </div>
        </Modal>
            <BatchCreateModal
                ref={batchCreateRef}
                open={batchModelVisible}
                onCancel={() =>{
                    Modal.confirm({
                        centered:true,
                        title: intl.formatMessage({ id: 'agent.modal.leave.title' }),
                        content: intl.formatMessage({ id: 'agent.modal.leave.content' }),
                        onOk: () => {
                            setBatchModelVisible(false)
                        },
                    });
                }}
                onOk={handleBatchCreate}
                loading={batchLoading}
                params={batchModelVisible}
                onReset={resetState}
            />
        </>
    );
});

export default AgentCreate;
