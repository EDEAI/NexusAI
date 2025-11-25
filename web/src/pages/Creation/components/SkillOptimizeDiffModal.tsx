import DiffViewer from '@/components/common/DiffViewer';
import { useIntl } from '@umijs/max';
import { Badge, Button, Modal, Spin, Tag } from 'antd';
import classNames from 'classnames';
import React, { useMemo } from 'react';

export interface SkillVariableInfo {
    name: string;
    type?: string;
    required?: boolean;
    display_name?: string;
    description?: string;
}

export interface SkillOptimizeData {
    name: string;
    description: string;
    input_variables: SkillVariableInfo[];
    dependencies: {
        python3: string[];
    };
    code: {
        python3: string;
    };
    output_type: number;
    output_variables: SkillVariableInfo[];
}

export interface SkillVariableComparison {
    name: string;
    current?: SkillVariableInfo;
    optimized?: SkillVariableInfo;
}

interface SkillOptimizeDiffModalProps {
    open: boolean;
    current?: SkillOptimizeData | null;
    optimized?: SkillOptimizeData | null;
    inputComparisons: SkillVariableComparison[];
    outputComparisons: SkillVariableComparison[];
    loading?: boolean;
    onApply: () => void;
    onCancel: () => void;
    onContinue?: () => void;
    applying?: boolean;
    continuing?: boolean;
    nameTitleOverride?: string;
    descriptionTitleOverride?: string;
    showOutputType?: boolean;
}

const SkillOptimizeDiffModal: React.FC<SkillOptimizeDiffModalProps> = ({
    open,
    current,
    optimized,
    inputComparisons,
    outputComparisons,
    loading = false,
    onApply,
    onCancel,
    onContinue,
    applying = false,
    continuing = false,
    nameTitleOverride,
    descriptionTitleOverride,
    showOutputType = true,
}) => {
    const intl = useIntl();
    const optimizedLoading = loading && !optimized;
    const headerLabel = useMemo(
        () => ({
            current: intl.formatMessage({ id: 'skill.optimize.diff.current' }),
            optimized: intl.formatMessage({ id: 'skill.optimize.diff.optimized' }),
        }),
        [intl],
    );
    const removedText = intl.formatMessage({ id: 'skill.optimize.diff.removed' });
    const addedText = intl.formatMessage({ id: 'skill.optimize.diff.added' });
    const nameTitle = nameTitleOverride || intl.formatMessage({ id: 'skill.appname' });
    const descriptionTitle =
        descriptionTitleOverride || intl.formatMessage({ id: 'skill.appdescription' });
    const inputsTitle = intl.formatMessage({ id: 'skill.optimize.diff.inputs' });
    const outputsTitle = intl.formatMessage({ id: 'skill.optimize.diff.outputs' });
    const dependenciesTitle = intl.formatMessage({ id: 'skill.optimize.diff.dependencies' });
    const codeTitle = intl.formatMessage({ id: 'skill.optimize.diff.code' });
    const outputTypeTitle = intl.formatMessage({ id: 'skill.outputvariable' });
    const emptyText = intl.formatMessage({ id: 'skill.optimize.diff.empty' });
    const varNameLabel = intl.formatMessage({ id: 'skill.optimize.diff.var.name' });
    const varDisplayLabel = intl.formatMessage({ id: 'skill.optimize.diff.var.display' });
    const varTypeLabel = intl.formatMessage({ id: 'skill.optimize.diff.var.type' });
    const varRequiredLabel = intl.formatMessage({ id: 'skill.optimize.diff.var.required' });
    const varDescLabel = intl.formatMessage({ id: 'skill.optimize.diff.var.description' });
    const depCurrentLabel = intl.formatMessage({
        id: 'skill.optimize.diff.dependencies.current',
    });
    const depOptimizedLabel = intl.formatMessage({
        id: 'skill.optimize.diff.dependencies.optimized',
    });
    const outputTypeLabel = intl.formatMessage({ id: 'skill.optimize.diff.outputType' });
    const continueText = intl.formatMessage({ id: 'skill.optimize.continue' });
    const applyText = intl.formatMessage({ id: 'skill.optimize.apply' });
    const cancelText = intl.formatMessage({ id: 'skill.optimize.cancel' });

    const footerButtons = [
        <Button key="cancel" onClick={onCancel} disabled={applying || continuing}>
            {cancelText}
        </Button>,
        onContinue ? (
            <Button
                key="continue"
                onClick={onContinue}
                disabled={applying}
                loading={continuing}
                type="default"
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

    const dependenciesCurrent = current?.dependencies?.python3 || [];
    const dependenciesOptimized = optimized?.dependencies?.python3 || [];
    const currentDepSet = new Set(dependenciesCurrent);
    const optimizedDepSet = new Set(dependenciesOptimized);

    const outputTypeMap = useMemo(
        () => ({
            1: intl.formatMessage({ id: 'skill.radio.text' }),
            2: intl.formatMessage({ id: 'skill.radio.database' }),
            3: intl.formatMessage({ id: 'skill.radio.code' }),
            4: intl.formatMessage({ id: 'skill.radio.file' }),
        }),
        [intl],
    );

    return (
        <Modal
            open={open}
            title={intl.formatMessage({ id: 'skill.optimize.diff.title' })}
            width={968}
            footer={footerButtons}
            onCancel={onCancel}
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
                                <div className="mt-1 text-sm font-medium text-blue-700">{optimized?.name ?? '--'}</div>
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

                <section className="space-y-4">
                    <h3 className="text-sm font-semibold text-gray-700">{inputsTitle}</h3>
                    <div className="space-y-4">
                        {optimizedLoading && (
                            <div className="rounded-lg border border-blue-200 bg-blue-50 p-6 flex justify-center">
                                <Spin />
                            </div>
                        )}
                        {!optimizedLoading && !inputComparisons.length && (
                            <div className="text-xs text-gray-500">{emptyText}</div>
                        )}
                        {!optimizedLoading &&
                            inputComparisons.map(item => {
                                const showRemovedOnly = !item.optimized && item.current;
                                const showAddedOnly = item.optimized && !item.current;
                                const currentVar = item.current;
                                const optimizedVar = item.optimized;
                                const renderVariableDetail = (
                                    variable?: SkillVariableInfo,
                                    label?: string,
                                ) => (
                                    <div>
                                        <div className="text-xs uppercase text-gray-500">{label}</div>
                                        <div className="mt-1 text-sm font-medium text-gray-900">
                                            {variable?.display_name || variable?.name || '--'}
                                        </div>
                                        <div className="flex flex-wrap gap-2 mt-2 text-xs text-gray-500">
                                            <Tag>{`${varNameLabel}: ${variable?.name || '--'}`}</Tag>
                                            <Tag color="blue">{`${varTypeLabel}: ${variable?.type || '--'}`}</Tag>
                                            <Tag color={variable?.required ? 'red' : 'default'}>
                                                {`${varRequiredLabel}: ${
                                                    variable?.required
                                                        ? intl.formatMessage({ id: 'agent.capabilitystatus.enable' }) ||
                                                          'Yes'
                                                        : intl.formatMessage({ id: 'agent.capabilitystatus.disable' }) ||
                                                          'No'
                                                }`}
                                            </Tag>
                                        </div>
                                        <div className="mt-2 text-xs text-gray-500">{varDescLabel}</div>
                                        <div className="text-sm text-gray-800 whitespace-pre-wrap">
                                            {variable?.description || '--'}
                                        </div>
                                    </div>
                                );

                                return (
                                    <div
                                        key={item.name}
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
                                            <Badge color="blue" text={`${varNameLabel}: ${item.name || '--'}`} />
                                            {showAddedOnly && <Tag color="green">{addedText}</Tag>}
                                            {showRemovedOnly && <Tag color="red">{removedText}</Tag>}
                                        </div>
                                        <div className="grid grid-cols-2 gap-4 text-xs">
                                            {renderVariableDetail(currentVar, headerLabel.current)}
                                            {renderVariableDetail(optimizedVar, headerLabel.optimized)}
                                        </div>
                                    </div>
                                );
                            })}
                    </div>
                </section>

                <section className="space-y-4">
                    <h3 className="text-sm font-semibold text-gray-700">{dependenciesTitle}</h3>
                    <Spin spinning={optimizedLoading}>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="rounded-lg border border-gray-200 p-3 min-h-[120px]">
                                <div className="text-xs uppercase text-gray-500 mb-2">{depCurrentLabel}</div>
                                <div className="flex flex-wrap gap-2">
                                    {dependenciesCurrent.length
                                        ? dependenciesCurrent.map(dep => (
                                              <Tag
                                                  key={`current-${dep}`}
                                                  color={optimizedDepSet.has(dep) ? undefined : 'red'}
                                              >
                                                  {dep}
                                              </Tag>
                                          ))
                                        : emptyText}
                                </div>
                            </div>
                            <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 min-h-[120px]">
                                <div className="text-xs uppercase text-gray-500 mb-2">{depOptimizedLabel}</div>
                                <div className="flex flex-wrap gap-2">
                                    {dependenciesOptimized.length
                                        ? dependenciesOptimized.map(dep => (
                                              <Tag
                                                  key={`optimized-${dep}`}
                                                  color={currentDepSet.has(dep) ? 'blue' : 'green'}
                                              >
                                                  {dep}
                                              </Tag>
                                          ))
                                        : emptyText}
                                </div>
                            </div>
                        </div>
                    </Spin>
                </section>

                <section className="space-y-3">
                    <h3 className="text-sm font-semibold text-gray-700">{codeTitle}</h3>
                    <Spin spinning={optimizedLoading}>
                        <DiffViewer original={current?.code?.python3 ?? ''} modified={optimized?.code?.python3 ?? ''} />
                    </Spin>
                </section>

                {showOutputType && (
                    <section className="space-y-4">
                        <h3 className="text-sm font-semibold text-gray-700">{outputTypeTitle}</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="rounded-lg border border-gray-200 p-3">
                                <div className="text-xs uppercase text-gray-500">{headerLabel.current}</div>
                                <div className="mt-1 text-sm font-medium text-gray-900">
                                    {outputTypeMap[current?.output_type as 1 | 2 | 3 | 4] || outputTypeLabel}
                                </div>
                            </div>
                            <Spin spinning={optimizedLoading}>
                                <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 min-h-[76px]">
                                    <div className="text-xs uppercase text-gray-500">{headerLabel.optimized}</div>
                                    <div className="mt-1 text-sm font-medium text-blue-700">
                                        {outputTypeMap[optimized?.output_type as 1 | 2 | 3 | 4] || outputTypeLabel}
                                    </div>
                                </div>
                            </Spin>
                        </div>
                    </section>
                )}

                <section className="space-y-4">
                    <h3 className="text-sm font-semibold text-gray-700">{outputsTitle}</h3>
                    <div className="space-y-4">
                        {optimizedLoading && (
                            <div className="rounded-lg border border-blue-200 bg-blue-50 p-6 flex justify-center">
                                <Spin />
                            </div>
                        )}
                        {!optimizedLoading && !outputComparisons.length && (
                            <div className="text-xs text-gray-500">{emptyText}</div>
                        )}
                        {!optimizedLoading &&
                            outputComparisons.map(item => {
                                const showRemovedOnly = !item.optimized && item.current;
                                const showAddedOnly = item.optimized && !item.current;
                                const currentVar = item.current;
                                const optimizedVar = item.optimized;

                                return (
                                    <div
                                        key={item.name}
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
                                            <Badge color="blue" text={`${varNameLabel}: ${item.name || '--'}`} />
                                            {showAddedOnly && <Tag color="green">{addedText}</Tag>}
                                            {showRemovedOnly && <Tag color="red">{removedText}</Tag>}
                                        </div>
                                        <div className="grid grid-cols-2 gap-4 text-xs">
                                            <div>
                                                <div className="text-xs uppercase text-gray-500">
                                                    {headerLabel.current}
                                                </div>
                                                <div className="mt-1 text-sm font-medium text-gray-900">
                                                    {currentVar?.display_name || currentVar?.name || '--'}
                                                </div>
                                                <div className="flex flex-wrap gap-2 mt-2 text-xs text-gray-500">
                                                    <Tag>{`${varNameLabel}: ${currentVar?.name || '--'}`}</Tag>
                                                    <Tag color="blue">{`${varTypeLabel}: ${
                                                        currentVar?.type || '--'
                                                    }`}</Tag>
                                                </div>
                                                <div className="mt-2 text-xs text-gray-500">{varDescLabel}</div>
                                                <div className="text-sm text-gray-800 whitespace-pre-wrap">
                                                    {currentVar?.description || '--'}
                                                </div>
                                            </div>
                                            <div>
                                                <div className="text-xs uppercase text-gray-500">
                                                    {headerLabel.optimized}
                                                </div>
                                                <div className="mt-1 text-sm font-medium text-blue-700">
                                                    {optimizedVar?.display_name || optimizedVar?.name || '--'}
                                                </div>
                                                <div className="flex flex-wrap gap-2 mt-2 text-xs text-gray-500">
                                                    <Tag color="blue">{`${varNameLabel}: ${
                                                        optimizedVar?.name || '--'
                                                    }`}</Tag>
                                                    <Tag color="green">{`${varTypeLabel}: ${
                                                        optimizedVar?.type || '--'
                                                    }`}</Tag>
                                                </div>
                                                <div className="mt-2 text-xs text-gray-500">{varDescLabel}</div>
                                                <div className="text-sm text-gray-800 whitespace-pre-wrap">
                                                    {optimizedVar?.description || '--'}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                    </div>
                </section>
            </div>
        </Modal>
    );
};

export default SkillOptimizeDiffModal;
