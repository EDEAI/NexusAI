import { BulbOutlined, SendOutlined } from '@ant-design/icons';
import { Button, InputNumber } from 'antd';
import { memo, useState } from 'react';
import { useIntl } from '@umijs/max';
import BeforeCreate from '../BeforeCreate';
import ResultDisplay, { PromptTextarea, ResultDisplayRef } from '../ResultDisplay';
import { AgentFormData, AgentResult } from '../types';

interface BatchCreateProps {
    loading: boolean;
    correctLoading?: boolean;
    regenerateLoading?: boolean;
    agentCreateResult: AgentResult | null;
    agentCreateResultOutput: AgentResult | null;
    resultDisplayRef: React.RefObject<ResultDisplayRef>;
    onFormChange: (values: AgentFormData) => void;
    onSubmit: (prompt: string, count: number) => void;
    onPreview?: (value: string) => void;
    prompt: string;
    onPromptChange: (value: string) => void;
}

const BatchCreate = memo(
    ({
        loading,
        correctLoading,
        regenerateLoading,
        agentCreateResult,
        agentCreateResultOutput,
        resultDisplayRef,
        onFormChange,
        onSubmit,
        onPreview,
        prompt,
        onPromptChange,
    }: BatchCreateProps) => {
        const intl = useIntl();
        const [count, setCount] = useState<number | null>(null);
        const [countError, setCountError] = useState(false);

        const handleSubmit = (prompt: string) => {
            if (!count || count < 1) {
                setCountError(true);
                return;
            }
            onSubmit(prompt, count);
        };

        return (
            <div className="flex gap-4 h-full relative flex-1">
                {!agentCreateResult ? (
                    <BeforeCreate type={'batch'} hasHover={false} loading={loading} />
                ) : (
                    <ResultDisplay
                        ref={resultDisplayRef}
                        initialValues={agentCreateResultOutput}
                        onChange={onFormChange}
                        readOnly={true}
                        loading={loading }
                    />
                )}
                <div className="w-1/2">
                    <PromptTextarea
                        placeholder={intl.formatMessage({ id: 'agent.create.prompt.batch' })}
                        submitText={intl.formatMessage({ id: 'agent.create.generate' })}
                        submitIcon={<SendOutlined />}
                        onSubmit={handleSubmit}
                        defaultValue={prompt}
                        onChange={onPromptChange}
                        renderButton={({ disabled, onClick, value }) => {
                            return (
                                <div className="flex gap-2 justify-between w-[calc(100%-20px)] ">
                                    <Button
                                        type="primary"
                                        color="primary"
                                        variant="filled"
                                        disabled={disabled}
                                        loading={loading}
                                        icon={<BulbOutlined />}
                                        onClick={() => onPreview?.(value)}
                                    >
                                        {intl.formatMessage({ id: 'agent.create.preview' })}
                                    </Button>
                                    <div className="flex gap-2">
                                        <InputNumber
                                            placeholder={intl.formatMessage({ id: 'agent.create.input.count' })}
                                            className={`w-[200px] ${
                                                countError
                                                    ? '!border-red-500 hover:!border-red-500 focus:!border-red-500'
                                                    : ''
                                            }`}
                                            status={countError ? 'error' : undefined}
                                            value={count}
                                            onChange={value => {
                                                setCount(value);
                                                setCountError(false);
                                            }}
                                            min={1}
                                        />
                                        <Button
                                            type="primary"
                                            disabled={disabled}
                                            onClick={onClick}
                                            icon={<SendOutlined />}
                                        >
                                            {intl.formatMessage({ id: 'agent.create.batch.generate' })}
                                        </Button>
                                    </div>
                                </div>
                            );
                        }}
                        className="h-full"
                        key="batch-prompt"
                    />
                </div>
            </div>
        );
    },
);

export default BatchCreate;
