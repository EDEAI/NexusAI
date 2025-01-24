import { ReloadOutlined, SaveOutlined, SendOutlined, ToolOutlined } from '@ant-design/icons';
import { Button, Tooltip } from 'antd';
import { memo } from 'react';
import { useIntl } from '@umijs/max';
import BeforeCreate from '../BeforeCreate';
import ResultDisplay, { PromptTextarea, ResultDisplayRef } from '../ResultDisplay';
import { AgentFormData, AgentResult } from '../types';

interface SingleCreateProps {
    loading: boolean;
    agentCreateResult: AgentResult | null;
    agentCreateResultOutput: AgentResult | null;
    correctVisible: boolean;
    prompt: string;
    conPrompt?:string;
    resultDisplayRef: React.RefObject<ResultDisplayRef>;
    onFormChange: (values: AgentFormData) => void;
    onSubmit: (prompt: string) => void;
    onRegenerate: () => void;
    onCorrect: (prompt: string) => void;
    onPromptChange: (value: string) => void;
    onCorrectVisibleChange: (visible: boolean) => void;
    onSave?: () => void;
}

const SingleCreate = memo(
    ({
        loading,
        agentCreateResult,
        agentCreateResultOutput,
        correctVisible,
        prompt,
        conPrompt,
        resultDisplayRef,
        onFormChange,
        onSubmit,
        onRegenerate,
        onCorrect,
        onPromptChange,
        onCorrectVisibleChange,
        onSave,
    }: SingleCreateProps) => {
        const intl = useIntl();

        return (
            <div className="flex gap-4 h-full relative flex-1">
                {!agentCreateResult ? (
                    <BeforeCreate type={'single'} hasHover={false} loading={loading} />
                ) : (
                    <div className="relative w-1/2">
                        <ResultDisplay
                            ref={resultDisplayRef}
                            initialValues={agentCreateResultOutput}
                            onChange={onFormChange}
                            loading={loading}
                        />
                        <div className="absolute bottom-2 right-2 flex gap-2 p-1  bg-opacity-50 rounded-md">
                            <Tooltip title={intl.formatMessage({ id: 'agent.create.tooltip.regenerate' })}>
                                <Button
                                    type="primary"
                                    color="primary"
                                    variant="filled"
                                    icon={<ReloadOutlined />}
                                    loading={loading}
                                    onClick={onRegenerate}
                                />
                            </Tooltip>
                            <Tooltip title={intl.formatMessage({ id: 'agent.create.tooltip.correct' })}>
                                <Button
                                    type="primary"
                                    color="primary"
                                    variant="filled"
                                    icon={<ToolOutlined />}
                                    loading={loading}
                                    onClick={() => onCorrectVisibleChange(true)}
                                />
                            </Tooltip>
                            <Tooltip title={intl.formatMessage({ id: 'agent.create.tooltip.save' })}>
                                <Button
                                    type="primary"
                                    variant="filled"
                                    icon={<SaveOutlined />}
                                    loading={loading}
                                    onClick={onSave}
                                />
                            </Tooltip>
                        </div>
                        {correctVisible && (
                            <div className="absolute bottom-2 right-2 w-[calc(100%-20px)] z-10">
                                <PromptTextarea
                                    placeholder={intl.formatMessage({ id: 'agent.create.prompt.modify' })}
                                    submitText={intl.formatMessage({ id: 'agent.create.button.modify' })}
                                    submitIcon={<ToolOutlined />}
                                    showCloseButton={true}
                                    className="h-[100px]"
                                    loading={loading}
                                    onClose={() => onCorrectVisibleChange(false)}
                                    defaultValue={conPrompt}
                                    onSubmit={onCorrect}
                                    submitButtonProps={{
                                        size: 'small',
                                        loading: loading,
                                    }}
                                    key="single-prompt"
                                />
                            </div>
                        )}
                    </div>
                )}
                <div className="w-1/2">
                    <PromptTextarea
                        placeholder={intl.formatMessage({ id: 'agent.create.prompt.single' })}
                        submitText={intl.formatMessage({ id: 'agent.create.generate' })}
                        submitIcon={<SendOutlined />}
                        className="h-full"
                        loading={loading}
                        defaultValue={prompt}
                        onChange={onPromptChange}
                        onSubmit={onSubmit}
                        key="single-prompt"
                    />
                </div>
            </div>
        );
    },
);

export default SingleCreate;
