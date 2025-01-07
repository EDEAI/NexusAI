import { agentGenerate, agentReGenerate } from '@/api/workflow';
import useUserStore from '@/store/user';
import useSocketStore from '@/store/websocket';
import { ReloadOutlined, SendOutlined, ToolOutlined } from '@ant-design/icons';
import { useRafState } from '@reactuses/core';
import { useUpdateEffect } from 'ahooks';
import { Button, Modal, Spin } from 'antd';
import { memo, useCallback, useState } from 'react';
import BatchCreate from './BatchCreate';
import ResultDisplay, { PromptTextarea } from './ResultDisplay';
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
    const [agentCreateResult, setAgentCreateResult] = useRafState<AgentResult | null>(null);
    const [agentCreateResultOutput, setAgentCreateResultVisibleOutput] =
        useState<AgentResult | null>(null);
    const [inputVisible, setInputVisible] = useState(true);
    const [promptVisible, setPromptVisible] = useState(false);
    const [formData, setFormData] = useState<AgentFormData | null>(null);
    const [batchVisible, setBatchVisible] = useState(false);
    const [batchLoading, setBatchLoading] = useState(false);
    const [generateId, setGenerateId] = useState(null);
    const [hasProcessed, setHasProcessed] = useState(false);
    const flowMessage = useSocketStore(state => state.flowMessage);

    useUpdateEffect(() => {
        if (agentCreateOpen) {
            setModelOpen(agentCreateOpen);
        }
    }, [agentCreateOpen]);

    const handleOk = () => {
        setAgentCreateOpen(false);
        setModelOpen(false);
    };

    const handleCancel = () => {
        setAgentCreateOpen(false);
        setModelOpen(false);
    };

    const handleSubmit = async (prompt: string) => {
        console.log(prompt);
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
        setLoading(true);
        try {
            const res = await agentReGenerate(generateId?.app_run_id);
            console.log(res);
            if (res.code == 0) {
                setHasProcessed(false);
                setGenerateId(res.data);
            }
        } finally {
        }
    };
    useUpdateEffect(() => {
        const currentMessage = flowMessage?.find(
            item => item?.data?.app_run_id == generateId?.app_run_id,
        );
        if (currentMessage && !hasProcessed) {
            setAgentCreateResultVisibleOutput(currentMessage?.data?.exec_data?.outputs?.value);
            setAgentCreateResult(currentMessage?.data);
            console.log(currentMessage?.data?.exec_data?.outputs?.value);

            setInputVisible(false);
            setPromptVisible(true);
            setLoading(false);
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

    const BeforeCreate = useCallback(
        () => (
            <div className="rounded-lg flex-1 border border-gray-200 p-4 bg-gray-50 flex justify-center items-center flex-col gap-2 text-[#1b64f3]">
                {/* {loading ? <div>生成中...</div> : <div>待生成智能体</div>} */}
                {loading ? (
                    <>
                        <Spin />
                        <div>生成中...</div>
                    </>
                ) : (
                    <>
                        <img src="/icons/agent_create.svg" className="size-16"></img>
                        <div>待生成智能体</div>
                    </>
                )}
            </div>
        ),
        [loading],
    );

    const RenderFooter = () => {
        return (
            <div className="flex gap-2 justify-between">
                <div className="flex gap-2 pl-4">
                    {agentCreateResult && (
                        <>
                            <Button onClick={handleRegenerateAgent} icon={<ReloadOutlined />}>
                                生成新智能体
                            </Button>
                            <Button
                                type="primary"
                                variant="filled"
                                color="primary"
                                onClick={() => setBatchVisible(true)}
                            >
                                批量生成智能体
                            </Button>
                        </>
                    )}
                </div>
                <div className="flex gap-2">
                    <Button onClick={handleCancel}>取消</Button>
                    <Button type="primary" onClick={handleOk}>
                        保存
                    </Button>
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
    };

    useUpdateEffect(() => {
        if (!modelOpen) {
            resetState();
        }
    }, [modelOpen]);

    return (
        <>
            <Modal
                title="创建智能体"
                className="xl:min-w-[1200px] lg:min-w-[1000px]"
                bodyProps={{
                    className: '!h-[600px] overflow-y-auto p-4',
                }}
                open={modelOpen}
                footer={RenderFooter}
                onOk={handleOk}
                onCancel={handleCancel}
            >
                <div className="flex gap-4 h-full">
                    {agentCreateResult ? (
                        <ResultDisplay
                            initialValues={agentCreateResultOutput}
                            onChange={handleFormChange}
                            loading={loading}
                        />
                    ) : (
                        <BeforeCreate />
                    )}
                    <div className="w-1/2 flex flex-col gap-4">
                        <PromptTextarea
                            placeholder="输入智能体生成提示词"
                            submitText="生成智能体"
                            submitIcon={<SendOutlined />}
                            loading={loading}
                            onSubmit={handleSubmit}
                            className="h-full"
                        ></PromptTextarea>
                        {agentCreateResult && (
                            <PromptTextarea
                                placeholder="输入智能体生成提示词"
                                submitText="修正智能体"
                                submitIcon={<ToolOutlined />}
                                className="h-full"
                            ></PromptTextarea>
                        )}
                    </div>
                </div>
            </Modal>
            <BatchCreate
                open={batchVisible}
                onCancel={() => setBatchVisible(false)}
                onOk={handleBatchCreate}
                loading={batchLoading}
            />
        </>
    );
});

export default AgentCreate;
