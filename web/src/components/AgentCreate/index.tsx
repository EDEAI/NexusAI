import {
    agentCreate,
    agentGenerate,
    agentReGenerate,
    agentSupplement,
    batchAgentCreate,
} from '@/api/workflow';
import useUserStore from '@/store/user';
import useSocketStore from '@/store/websocket';
import {
    ArrowLeftOutlined,
    PullRequestOutlined,
    ReloadOutlined,
    SendOutlined,
    ToolOutlined,
} from '@ant-design/icons';
import { ProFormDigit } from '@ant-design/pro-components';
import { useRafState } from '@reactuses/core';
import { useUpdateEffect } from 'ahooks';
import { App, Button, Modal, message } from 'antd';
import { memo, useCallback, useRef, useState } from 'react';
import BatchCreate, { BatchCreateRef } from './BatchCreate';
import BeforeCreate from './BeforeCreate';
import { PromptTextarea, ResultDisplayRef } from './ResultDisplay';
import { AgentFormData, AgentResult, BatchCreateFormData } from './types';

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
    const [loading, setLoading] = useState(false);
    const [correctLoading, setCorrectLoading] = useState(false);
    const [regenerateLoading, setRegenerateLoading] = useState(false);
    const [agentCreateResult, setAgentCreateResult] = useRafState<AgentResult | null>(null);
    const [agentCreateResultOutput, setAgentCreateResultVisibleOutput] =
        useState<AgentResult | null>(null);
    const [inputVisible, setInputVisible] = useState(true);
    const [promptVisible, setPromptVisible] = useState(false);
    const [formData, setFormData] = useState<AgentFormData | null>(null);
    const [batchVisible, setBatchVisible] = useState(false);
    const [batchModelVisible, setBatchModelVisible] = useState(false);

    const [batchLoading, setBatchLoading] = useState(false);
    const [generateId, setGenerateId] = useState(null);
    const [hasProcessed, setHasProcessed] = useState(false);
    const flowMessage = useSocketStore(state => state.flowMessage);
    const resultDisplayRef = useRef<ResultDisplayRef>(null);
    const [batchCount, setBatchCount] = useState(10);
    const { modal } = App.useApp();
    const batchCreateRef = useRef<BatchCreateRef>(null);
    const [createType, setCreateType] = useState<'single' | 'batch' | ''>('');
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
        try {
            const res = await agentCreate(createParams);
            console.log(res);
            if (res.code == 0) {
                message.success('智能体创建成功');
            }
        } finally {
        }
    };

    const closeModal = () => {
        if (agentCreateResult) {
            Modal.confirm({
                title: '提示',
                content: '是否确认离开？',
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

    const handleSubmit = async (prompt: string) => {
        setLoading(true);
        try {
            const res = await agentGenerate(prompt);
            console.log(res);
            if (res.code == 0) {
                setHasProcessed(false);
                setGenerateId(res.data);
                // setAgentCreateResult(res.data)
            }
        } finally {
        }
    };
    const handleRegenerateAgent = async () => {
        if (!generateId?.app_run_id) return;
        setRegenerateLoading(true);
        try {
            const res = await agentReGenerate(generateId?.app_run_id);

            if (res.code == 0) {
                console.log(res);
                setHasProcessed(false);
                setGenerateId(res.data);
            }
        } finally {
        }
    };
    const handleCorrectAgent = async prompt => {
        if (!generateId?.app_run_id) return;
        setCorrectLoading(true);
        try {
            const res = await agentSupplement(prompt, generateId?.app_run_id);

            if (res.code == 0) {
                console.log(res);
                setHasProcessed(false);
                setGenerateId(res.data);
            }
        } finally {
        }
    };

    const handleBatchGenerate = async (prompt: string) => {
        setBatchLoading(true);
        const params = {
            app_run_id: generateId?.app_run_id,
            loop_count: 10,
            loop_limit: batchCount,
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
                setBatchVisible(false);
            }, 100);
        }
    };
    useUpdateEffect(() => {
        const currentMessage = flowMessage?.find(
            item =>
                item?.data?.app_run_id == generateId?.app_run_id &&
                item?.data?.exec_data?.exec_id == generateId?.record_id,
        );
        if (currentMessage && !hasProcessed) {
            try {
                setAgentCreateResultVisibleOutput(
                    JSON.parse(currentMessage?.data?.exec_data?.outputs?.value),
                );
            } catch (e) {
                console.log(e);
            }
            setAgentCreateResult(currentMessage?.data);
            setInputVisible(false);
            setPromptVisible(true);
            setLoading(false);
            setRegenerateLoading(false);
            setCorrectLoading(false);
            setHasProcessed(true);
        }
    }, [flowMessage, generateId]);

    const handleFormChange = (values: AgentFormData) => {
        setFormData(values);
    };

    const handleBatchCreate = async (data: BatchCreateFormData) => {
        setBatchLoading(true);
        try {
            const prompts = data.prompts.split('\n');
            const results = await Promise.all(
                Array(data.count)
                    .fill(0)
                    .map(() =>
                        Promise.all(
                            prompts.map(prompt => {
                                const finalPrompt = data.additionalPrompt
                                    ? `${prompt}\n${data.additionalPrompt}`
                                    : prompt;
                                return new Promise(resolve => setTimeout(resolve, 1000));
                            }),
                        ),
                    ),
            );
            // setBatchVisible(false);
        } finally {
            setBatchLoading(false);
        }
    };

    const RenderFooter = () => {
        return (
            <div className="flex gap-2 justify-between">
                <div className="flex gap-2 pl-4">
                    {agentCreateResult && (
                        <>
                            <Button
                                loading={regenerateLoading}
                                onClick={handleRegenerateAgent}
                                icon={<ReloadOutlined />}
                            >
                                生成新智能体
                            </Button>
                            {batchVisible ? (
                                <Button
                                    type="primary"
                                    variant="filled"
                                    icon={<ArrowLeftOutlined />}
                                    color="primary"
                                    onClick={() => setBatchVisible(false)}
                                >
                                    继续编辑
                                </Button>
                            ) : (
                                <Button
                                    type="primary"
                                    variant="filled"
                                    color="primary"
                                    onClick={() => setBatchVisible(true)}
                                >
                                    批量生成
                                </Button>
                            )}
                        </>
                    )}
                </div>
                <div className="flex gap-2">
                    {/* <Button onClick={handleCancel}>取消</Button> */}
                    {false && (
                        <Button
                            type="primary"
                            disabled={!agentCreateResult}
                            icon={<PullRequestOutlined />}
                            onClick={handleOk}
                        >
                            创建
                        </Button>
                    )}
                </div>
            </div>
        );
    };

    const resetState = () => {
        setHasProcessed(false);
        setGenerateId(null);
        setAgentCreateResult(null);
        setInputVisible(true);
        setPromptVisible(false);
        setBatchVisible(false);
        setBatchModelVisible(false);
        setBatchCount(10);
        setBatchLoading(false);
        setPrompt('');
        setLoading(false);
        setCorrectLoading(false);
        setRegenerateLoading(false);
        setAgentCreateResultVisibleOutput(null);
        setCreateType('');
    };

    const SelectedType = useCallback(() => {
        if (createType === 'single') {
            return (
                <div className="flex gap-4 h-full relative flex-1">
                    <BeforeCreate type={'single'} hasHover={false} loading={false} />
                    <div className="w-1/2">
                        <PromptTextarea
                            placeholder="输入智能体生成提示词"
                            submitText="生成智能体"
                            submitIcon={<SendOutlined />}
                            className="h-full"
                            loading={loading}
                            onSubmit={handleSubmit}
                            key="single-prompt"
                        ></PromptTextarea>
                    </div>
                </div>
            );
        }

        return (
            <div className="flex gap-4 h-full relative flex-1">
                <BeforeCreate type={'batch'} hasHover={false} loading={false} />
                <div className="w-1/2">
                    <PromptTextarea
                        placeholder="输入智能体批量生成提示词"
                        submitText="生成智能体"
                        submitIcon={<SendOutlined />}
                        className="h-full"
                        key="batch-prompt"
                    ></PromptTextarea>
                </div>
            </div>
        );
    }, [createType]);

    return (
        <>
            <Modal
                title="AI创建智能体"
                className="xl:min-w-[1200px] lg:min-w-[1000px]"
                bodyProps={{
                    className: '!h-[600px] overflow-y-auto p-4',
                }}
                open={modelOpen}
                footer={RenderFooter}
                onOk={handleOk}
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
                    {/* {agentCreateResult ? (
                        <ResultDisplay
                            ref={resultDisplayRef}
                            initialValues={agentCreateResultOutput}
                            onChange={handleFormChange}
                            loading={loading || correctLoading || regenerateLoading}
                        />
                    ) : (
                        <BeforeCreate type={batchVisible ? 'batch' : 'single'} loading={true} />
                    )} */}

                    <div className="flex flex-col gap-4 relative">
                        {/* <PromptTextarea
                            placeholder="输入智能体生成提示词"
                            submitText="生成智能体"
                            submitIcon={<SendOutlined />}
                            loading={loading}
                            onSubmit={handleSubmit}
                            className="h-full"
                            key="single-prompt"
                        ></PromptTextarea> */}
                        {agentCreateResult && (
                            <PromptTextarea
                                placeholder="输入智能体生成提示词"
                                submitText="修正智能体"
                                submitIcon={<ToolOutlined />}
                                onSubmit={handleCorrectAgent}
                                className="h-full"
                                loading={correctLoading}
                                key="single-prompt"
                            ></PromptTextarea>
                        )}
                        {batchVisible && (
                            <div className="absolute w-full h-full bg-white left-0 top-0 flex flex-col gap-4">
                                <ProFormDigit
                                    label="生成数量"
                                    min={1}
                                    initialValue={10}
                                    layout="vertical"
                                    formItemProps={{
                                        className: 'mb-0',
                                    }}
                                    fieldProps={{
                                        precision: 0,
                                        step: 1,
                                        onChange: value => setBatchCount(Number(value)),
                                        controls: true,
                                        parser: value => Math.floor(Number(value || 0)),
                                        formatter: value => `${value}`.replace(/[^\d]/g, ''),
                                    }}
                                />
                                <PromptTextarea
                                    placeholder="输入批量生成提示词"
                                    submitText="开始批量生成"
                                    submitIcon={<SendOutlined />}
                                    loading={loading}
                                    onSubmit={handleBatchGenerate}
                                    className="h-full"
                                    key="batch-prompt"
                                ></PromptTextarea>
                            </div>
                        )}
                    </div>
                </div>
            </Modal>
            <BatchCreate
                ref={batchCreateRef}
                open={!!batchModelVisible}
                onCancel={() => setBatchModelVisible(false)}
                onOk={handleBatchCreate}
                loading={batchLoading}
                params={batchModelVisible}
                onReset={resetState}
            />
        </>
    );
});

export default AgentCreate;
