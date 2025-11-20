import DiffViewer from '@/components/common/DiffViewer';
import type { AgentCorrectAbility } from '@/api/workflow';
import { useIntl } from '@umijs/max';
import { Badge, Button, Modal, Spin, Tag } from 'antd';
import classNames from 'classnames';
import React, { useMemo } from 'react';

interface NormalizedAbility extends AgentCorrectAbility {
    index?: number;
}

export interface AbilityComparison {
    agent_ability_id: number;
    index: number;
    current?: NormalizedAbility;
    optimized?: NormalizedAbility;
}

interface AgentOptimizeData {
    name: string;
    description: string;
    obligations: string;
    abilities: NormalizedAbility[];
}

interface AgentOptimizeDiffModalProps {
    open: boolean;
    current?: AgentOptimizeData | null;
    optimized?: AgentOptimizeData | null;
    loading?: boolean;
    abilityComparisons: AbilityComparison[];
    onApply: () => void;
    onCancel: () => void;
    onContinue?: () => void;
    applying?: boolean;
    continuing?: boolean;
}

const statusColor = (status?: number) => {
    if (status === 1) return 'green';
    if (status === 2) return 'red';
    return 'default';
};

const AgentOptimizeDiffModal: React.FC<AgentOptimizeDiffModalProps> = ({
    open,
    current,
    optimized,
    loading = false,
    abilityComparisons,
    onApply,
    onCancel,
    applying = false,
    onContinue,
    continuing = false,
}) => {
    const intl = useIntl();

    const outputFormatText = useMemo(
        () => ({
            0: intl.formatMessage({ id: 'agent.optimize.diff.output.default' }),
            1: intl.formatMessage({ id: 'agent.optimize.diff.output.text' }),
            2: intl.formatMessage({ id: 'agent.optimize.diff.output.json' }),
            3: intl.formatMessage({ id: 'agent.optimize.diff.output.code' }),
        }),
        [intl],
    );

    const headerLabel = useMemo(
        () => ({
            current: intl.formatMessage({ id: 'agent.optimize.diff.current' }),
            optimized: intl.formatMessage({ id: 'agent.optimize.diff.optimized' }),
        }),
        [intl],
    );

    const statusLabel = useMemo(
        () => ({
            enabled: intl.formatMessage({ id: 'agent.capabilitystatus.enable' }),
            disabled: intl.formatMessage({ id: 'agent.capabilitystatus.disable' }),
        }),
        [intl],
    );

    const abilityTitle = intl.formatMessage({ id: 'agent.optimize.diff.abilities' });
    const nameTitle = intl.formatMessage({ id: 'agent.appname' });
    const descriptionTitle = intl.formatMessage({ id: 'agent.appdescription' });
    const obligationTitle = intl.formatMessage({ id: 'agent.functiondescription' });
    const applyText = intl.formatMessage({ id: 'agent.optimize.apply' });
    const cancelText = intl.formatMessage({ id: 'agent.optimize.cancel' });
    const removedText = intl.formatMessage({ id: 'agent.optimize.diff.removed' });
    const addedText = intl.formatMessage({ id: 'agent.optimize.diff.added' });
    const abilityIdLabel = intl.formatMessage({ id: 'agent.optimize.diff.ability.id' });
    const statusTitle = intl.formatMessage({ id: 'agent.capabilitystatus' });
    const outputTitle = intl.formatMessage({ id: 'agent.enableall' });
    const continueText = intl.formatMessage({ id: 'agent.optimize.continue' });
    const optimizedLoading = loading && !optimized;

    const footerButtons = [
        <Button key="cancel" onClick={onCancel} disabled={applying || continuing}>
            {cancelText}
        </Button>,
        onContinue ? (
            <Button
                key="continue"
                type="default"
                onClick={onContinue}
                loading={continuing}
                disabled={applying}
            >
                {continueText}
            </Button>
        ) : null,
        <Button
            key="apply"
            type="primary"
            onClick={onApply}
            loading={applying}
            disabled={continuing}
        >
            {applyText}
        </Button>,
    ].filter(Boolean);

    return (
        <Modal
            open={open}
            title={intl.formatMessage({ id: 'agent.optimize.diff.title' })}
            width={968}
            onCancel={onCancel}
            footer={footerButtons}
            destroyOnClose
            bodyStyle={{ maxHeight: '70vh', overflowY: 'auto' }}
        >
            <div className="space-y-6 py-2">
                <section className="space-y-3">
                    <h3 className="text-sm font-semibold text-gray-700">{nameTitle}</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="rounded-lg border border-gray-200 p-3">
                            <div className="text-xs uppercase text-gray-500">{headerLabel.current}</div>
                            <div className="mt-1 text-sm font-medium text-gray-900">{current?.name ?? '--'}</div>
                        </div>
                        <Spin spinning={optimizedLoading}>
                            <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 min-h-[76px]">
                                <div className="text-xs uppercase text-gray-500">{headerLabel.optimized}</div>
                                <div className="mt-1 text-sm font-medium text-blue-700">
                                    {optimized?.name ?? '--'}
                                </div>
                            </div>
                        </Spin>
                    </div>
                </section>

                <section className="space-y-3">
                    <h3 className="text-sm font-semibold text-gray-700">{descriptionTitle}</h3>
                    <Spin spinning={optimizedLoading}>
                        <DiffViewer original={current?.description ?? ''} modified={optimized?.description ?? ''} />
                    </Spin>
                </section>

                <section className="space-y-3">
                    <h3 className="text-sm font-semibold text-gray-700">{obligationTitle}</h3>
                    <Spin spinning={optimizedLoading}>
                        <DiffViewer original={current?.obligations ?? ''} modified={optimized?.obligations ?? ''} />
                    </Spin>
                </section>

                <section className="space-y-4">
                    <h3 className="text-sm font-semibold text-gray-700">{abilityTitle}</h3>
                    <div className="space-y-4">
                        {optimizedLoading && (
                            <div className="rounded-lg border border-blue-200 bg-blue-50 p-6 flex justify-center">
                                <Spin />
                            </div>
                        )}
                        {!optimizedLoading && (
                            <>
                                {abilityComparisons.map(item => {
                                    const idLabel =
                                        item.agent_ability_id && item.agent_ability_id > 0
                                            ? `#${item.agent_ability_id}`
                                            : intl.formatMessage({ id: 'agent.optimize.diff.ability.new' });

                                    const showRemovedOnly = !item.optimized && item.current;
                                    const showAddedOnly = item.optimized && !item.current;

                                    return (
                                        <div
                                    key={`${item.index}-${item.agent_ability_id}`}
                                    className={classNames(
                                        'rounded-lg border p-4 space-y-3',
                                        showAddedOnly
                                            ? 'border-green-200 bg-green-50'
                                            : showRemovedOnly
                                            ? 'border-red-200 bg-red-50'
                                            : 'border-gray-200 bg-white',
                                    )}
                                >
                                    <div className="flex flex-wrap items-center gap-2">
                                        <Badge color="blue" text={`${abilityIdLabel}: ${idLabel}`} />
                                        {showAddedOnly && (
                                            <Tag color="green">{addedText}</Tag>
                                        )}
                                        {showRemovedOnly && (
                                            <Tag color="red">{removedText}</Tag>
                                        )}
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <div className="text-xs uppercase text-gray-500">
                                                {headerLabel.current}
                                            </div>
                                            <div className="mt-1 text-sm font-medium text-gray-900">
                                                {item.current?.name ?? '--'}
                                            </div>
                                        </div>
                                        <div>
                                            <div className="text-xs uppercase text-gray-500">
                                                {headerLabel.optimized}
                                            </div>
                                            <div className="mt-1 text-sm font-medium text-blue-700">
                                                {item.optimized?.name ?? '--'}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4 text-xs">
                                        <div className="space-y-1">
                                            <div className="text-gray-500">{statusTitle}</div>
                                            {item.current && (
                                                <Tag color={statusColor(item.current.status as number)}>
                                                    {item.current.status === 1
                                                        ? statusLabel.enabled
                                                        : statusLabel.disabled}
                                                </Tag>
                                            )}
                                        </div>
                                        <div className="space-y-1">
                                            <div className="text-gray-500">{statusTitle}</div>
                                            {item.optimized && (
                                                <Tag color={statusColor(item.optimized.status as number)}>
                                                    {item.optimized.status === 1
                                                        ? statusLabel.enabled
                                                        : statusLabel.disabled}
                                                </Tag>
                                            )}
                                        </div>
                                        <div className="space-y-1">
                                            <div className="text-gray-500">{outputTitle}</div>
                                            {item.current && (
                                                <Tag>
                                                    {outputFormatText[item.current.output_format ?? 0]}
                                                </Tag>
                                            )}
                                        </div>
                                        <div className="space-y-1">
                                            <div className="text-gray-500">{outputTitle}</div>
                                            {item.optimized && (
                                                <Tag color="blue">
                                                    {outputFormatText[item.optimized.output_format ?? 0]}
                                                </Tag>
                                            )}
                                        </div>
                                    </div>
                                    <DiffViewer
                                        original={item.current?.content ?? ''}
                                        modified={item.optimized?.content ?? ''}
                                    />
                                </div>
                                    );
                                })}
                            </>
                        )}
                    </div>
                </section>
            </div>
        </Modal>
    );
};

export default AgentOptimizeDiffModal;
