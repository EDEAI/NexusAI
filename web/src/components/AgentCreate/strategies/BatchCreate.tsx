import { BulbOutlined, SendOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Button, InputNumber, Segmented, Tooltip } from 'antd';
import { memo, useState } from 'react';
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
    onSubmit: (prompt: string, count: number, batchCount: string) => void;
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
        const [batchCount, setBatchCount] = useState('10');

        const handleSubmit = (prompt: string) => {
            if (!count || count < 1) {
                setCountError(true);
                return;
            }
            onSubmit(prompt, count,batchCount);
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
                        loading={loading}
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
                                            placeholder={intl.formatMessage({
                                                id: 'agent.create.input.count',
                                            })}
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
                                        <Tooltip title={intl.formatMessage({ id: 'agent.batch.count.tooltip' })}>
                                            <Segmented<string>
                                                options={['3', '5', '10']}
                                                value={batchCount}
                                                onChange={value => {
                                                    setBatchCount(value);
                                                    console.log('Selected batch count:', value);
                                                }}
                                            />
                                        </Tooltip>
                                        <Button
                                            type="primary"
                                            disabled={disabled}
                                            onClick={onClick}
                                            icon={<SendOutlined />}
                                        >
                                            {intl.formatMessage({
                                                id: 'agent.create.batch.generate',
                                            })}
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
