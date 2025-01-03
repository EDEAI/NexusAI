/*
 * @LastEditors: biz
 */
/*
 * @LastEditors: biz
 */
import { CloseOutlined, ReloadOutlined, SendOutlined, ToolOutlined } from '@ant-design/icons';
import { useAutoAnimate } from '@formkit/auto-animate/react';
import { Button, Modal, Tooltip } from 'antd';
import { memo, useCallback, useState } from 'react';
import BatchCreate from './BatchCreate';
import ResultDisplay from './ResultDisplay';
import { AgentFormData, BatchCreateFormData } from './types';

interface PromptInputProps {
    value?: string;
    onChange?: (value: string) => void;
    onSubmit?: () => void;
    placeholder?: string;
    disabled?: boolean;
    buttonLoading?: boolean;
    isVisible?: boolean;
    onVisibleChange?: (visible: boolean) => void;
    buttonText?: string;
    buttonIcon?: React.ReactNode;
    triggerIcon?: React.ReactNode;
    triggerButtonProps?: React.ComponentProps<typeof Button>;
    submitButtonProps?: React.ComponentProps<typeof Button>;
    triggerButtonClassName?: string;
    triggerTooltip?: string;
    showCloseButton?: boolean;
}

const PromptInput = memo(
    ({
        value = '',
        onChange,
        onSubmit,
        placeholder = '请输入Agent生成提示词',
        disabled = false,
        buttonLoading = false,
        isVisible = false,
        onVisibleChange,
        buttonText = '生成Agent',
        buttonIcon = <SendOutlined />,
        triggerIcon = <SendOutlined />,
        triggerButtonProps,
        submitButtonProps,
        triggerButtonClassName = 'shrink-0 absolute right-6',
        triggerTooltip,
        showCloseButton = true,
    }: PromptInputProps) => {
        const [parent] = useAutoAnimate<HTMLDivElement>({
            duration: 300,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
        } as any);

        return (
            <div className={isVisible ? 'flex-1' : ''}>
                {isVisible ? (
                    <div
                        className={`relative !h-[calc(100%-50px)] ${
                            isVisible ? 'opacity-100' : '!opacity-0'
                        }`}
                    >
                        {showCloseButton && (
                            <Button
                                type="link"
                                icon={<CloseOutlined />}
                                onClick={() => onVisibleChange?.(false)}
                                className="absolute right-2 top-2 z-10"
                            />
                        )}
                        <textarea
                            className="w-full !h-full p-3 pr-9 rounded-lg border border-gray-200 resize-none outline-none focus:border-blue-500 transition-colors"
                            value={value}
                            onChange={e => onChange?.(e.target.value)}
                            placeholder={placeholder}
                        />
                        <div className="mt-2">
                            <Button
                                type="primary"
                                loading={buttonLoading}
                                icon={buttonIcon}
                                onClick={onSubmit}
                                className="w-full"
                                {...submitButtonProps}
                            >
                                {buttonText}
                            </Button>
                        </div>
                    </div>
                ) : (
                    <Tooltip title={triggerTooltip} placement="left">
                        <Button
                            type="primary"
                            icon={triggerIcon}
                            onClick={() => onVisibleChange?.(true)}
                            className={triggerButtonClassName}
                            {...triggerButtonProps}
                        />
                    </Tooltip>
                )}
            </div>
        );
    },
);

interface AgentResult {
    name: string;
    description: string;
    prompt: string;
    tools: string[];
}

const AgentCreate = memo(() => {
    const [isModalOpen, setIsModalOpen] = useState(true);
    const [prompt, setPrompt] = useState('');
    const [loading, setLoading] = useState(false);
    const [agentCreateResult, setAgentCreateResult] = useState<AgentResult | null>(null);
    const [inputVisible, setInputVisible] = useState(true);
    const [promptVisible, setPromptVisible] = useState(false);
    const [formData, setFormData] = useState<AgentFormData | null>(null);
    const [batchVisible, setBatchVisible] = useState(false);
    const [batchLoading, setBatchLoading] = useState(false);

    const handleOk = () => {
        setIsModalOpen(false);
    };

    const handleCancel = () => {
        setIsModalOpen(false);
    };

    const handleSubmit = async () => {
        if (!prompt.trim()) return;
        setLoading(true);
        try {
            await new Promise(resolve => setTimeout(resolve, 5000));
            setAgentCreateResult({
                name: '智能客服助手',
                description: '一个专业的客服助手，能够处理客户咨询和投诉',
                prompt: '你是一个专业的客服助手，负责...',
                tools: ['对话管理', '知识库查询', '情绪分析'],
            });
            setInputVisible(false);
        } finally {
            setLoading(false);
        }
    };

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
            setBatchVisible(false);
        } finally {
            setBatchLoading(false);
        }
    };

    const BeforeCreate = useCallback(
        () => (
            <div className="rounded-lg flex-1 border border-gray-200 p-4 bg-gray-50 flex justify-center items-center flex-col gap-2 text-[#1b64f3]">
                <img src="/icons/plaza_m2_c1.svg" className="size-16"></img>
                {loading ? <div>生成中...</div> : <div>待生成智能体</div>}
            </div>
        ),
        [loading],
    );

    const RenderFooter = () => {
        return (
            <div className="flex gap-2 justify-between">
                <div className="flex gap-2 pl-4">
                    {agentCreateResult && (
                        <Button onClick={() => setBatchVisible(true)}>批量生成智能体</Button>
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

    return (
        <>
            <Modal
                title="创建智能体"
                className="min-w-[1000px]"
                bodyProps={{
                    className: '!h-[600px] overflow-y-auto p-4',
                }}
                open={isModalOpen}
                footer={RenderFooter}
                onOk={handleOk}
                onCancel={handleCancel}
            >
                <div className="flex gap-4 h-full">
                    {agentCreateResult ? (
                        <ResultDisplay
                            initialValues={{
                                name: agentCreateResult.name,
                                description: agentCreateResult.description,
                                prompt: agentCreateResult.prompt,
                                skill_list: agentCreateResult.tools.map(tool => ({
                                    skill: tool,
                                    description: '一个简单的技能描述',
                                    output_format: 'json',
                                })),
                            }}
                            onChange={handleFormChange}
                            loading={loading}
                        />
                    ) : (
                        <BeforeCreate />
                    )}
                    {!promptVisible && (
                        <PromptInput
                            isVisible={inputVisible}
                            onVisibleChange={setInputVisible}
                            value={prompt}
                            onChange={setPrompt}
                            onSubmit={handleSubmit}
                            buttonLoading={loading}
                            showCloseButton={!!agentCreateResult}
                            triggerTooltip="生成智能体"
                        />
                    )}
                    {agentCreateResult && !inputVisible && (
                        <PromptInput
                            isVisible={promptVisible}
                            onVisibleChange={setPromptVisible}
                            value={prompt}
                            triggerButtonClassName="absolute right-6 mt-10"
                            onChange={setPrompt}
                            onSubmit={handleSubmit}
                            buttonLoading={loading}
                            buttonText={'修正智能体'}
                            triggerIcon={<ToolOutlined />}
                            buttonIcon={<ToolOutlined />}
                            triggerTooltip="修正智能体"
                            placeholder="请输入修正智能体提示词"
                        />
                    )}
                    {agentCreateResult && !inputVisible && !promptVisible && (
                        <Tooltip title={`重新生成智能体`} placement="left">
                            <Button
                                variant="filled"
                                type="primary"
                                icon={<ReloadOutlined />}
                                onClick={() => {}}
                                className="absolute right-6 mt-20 "
                            />
                        </Tooltip>
                    )}
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
