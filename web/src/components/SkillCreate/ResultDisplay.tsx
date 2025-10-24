import { ProForm, ProFormRadio, ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Spin, Typography } from 'antd';
import { forwardRef, memo, useCallback, useEffect, useImperativeHandle, useState } from 'react';
import TagSearch from '../TagSearch';
import Variable from '../WorkFlow/components/Variable';

const { Paragraph } = Typography;

interface SkillFormData {
    name: string;
    description: string;
    input_variables: Record<string, any>;
    dependencies: Record<string, any>;
    code: Record<string, any>;
    output_type: number;
    output_variables: Record<string, any>;
    test_input: Record<string, any>;
}

export interface ResultDisplayRef {
    getValue: () => Partial<SkillFormData>;
}

const ResultDisplay = memo(
    forwardRef<
        ResultDisplayRef,
        {
            initialValues?: Partial<SkillFormData>;
            onChange?: (values: Partial<SkillFormData>) => void;
            loading?: boolean;
            readOnly?: boolean;
        }
    >(({ initialValues, onChange, loading, readOnly = false }, ref) => {
        const intl = useIntl();
        const [values, setValues] = useState<Partial<SkillFormData>>(initialValues || {});

        useEffect(() => {
            setValues(prev => ({
                ...initialValues,
                tags: prev.tags || [],
            }));
        }, [initialValues]);

        useImperativeHandle(ref, () => ({
            getValue: () => values,
        }));

        const handleChange = (updates: Partial<SkillFormData>) => {
            if (readOnly) return;
            const newValues = { ...values, ...updates };
            console.log('values', newValues);
            
            setValues(newValues);
            onChange?.(newValues);
        };

        const handleVariableChange = (type: 'input' | 'output') => (data: { value: any[]; free: any }) => {
            const properties = data.value.reduce((acc, cur) => ({
                ...acc,
                [cur.name]: cur
            }), {});

            if (type === 'input') {
                handleChange({
                    input_variables: {
                        ...values.input_variables,
                        properties
                    }
                });
            } else {
                handleChange({
                    output_variables: {
                        ...values.output_variables,
                        properties
                    }
                });
            }
        };

        const handleDependenciesChange = (deps: string[]) => {
            handleChange({
                dependencies: {
                    python3: deps
                }
            });
        };

    return (
        <div className="flex-1 h-full pb-4 overflow-auto rounded-lg border border-gray-200 px-4 bg-gray-50 overflow-y-auto">
            <Spin
                spinning={loading}
                className="h-full"
                wrapperClassName="!h-full"
                tip="loading..."
                >
                    <div className="h-full pb-10">
                        <div className="px-4 pt-6 flex items-center gap-2">
                            <Paragraph
                                editable={
                                    !readOnly
                                        ? {
                                              onChange: value => handleChange({ name: value }),
                                              text: values.name,
                                              triggerType: ['text'],
                                              autoSize: true,
                                          }
                                        : false
                                }
                                className={`${
                                    !readOnly ? 'hover:bg-blue-100' : ''
                                } !mb-0 relative rounded-lg text-blue-600 text-[16px] flex items-center`}
                            >
                                <img
                                    src="/icons/agent_create.svg"
                                    className="size-6 mr-1"
                                ></img>
                                {values.name}
                            </Paragraph>
                        </div>
                        <div className="px-4 py-1 mt-2">
                            <Paragraph
                                editable={
                                    !readOnly
                                        ? {
                                              onChange: value =>
                                                  handleChange({ description: value }),
                                              text: values.description,
                                              triggerType: ['text'],
                                              autoSize: true,
                                          }
                                        : false
                                }
                                className={`${
                                    !readOnly ? 'hover:bg-blue-100' : ''
                                } rounded-lg !mb-0 text-[#666666] text-[12px]`}
                            >
                                {values.description}
                            </Paragraph>
                            {!readOnly && (
                                <div className="flex items-center hover:bg-blue-100 rounded-lg  mt-2">
                                    <img src="/icons/tag.svg" className="size-4"></img>
                                    <div className=" flex-1">
                                        <TagSearch
                                            showAddButton={false}
                                            className="w-full"
                                            variant="borderless"
                                            disabled={readOnly}
                                            onChange={tags => {
                                                handleChange({ tags });
                                            }}
                                            listStyle="horizontal"
                                            maxTagCount={20}
                                            value={values.tags}
                                        ></TagSearch>
                                    </div>
                                </div>
                            )}

                            <div>
                                <Variable
                                    variables={Object.values(values.input_variables?.properties || {})}
                                    title={intl.formatMessage({ id: 'skill.result.input.variables' })}
                                    onChange={handleVariableChange('input')}
                                    variableTypes={['string', 'number', 'json']}
                                    showDescription
                                />
                            </div>
                            {/* <div className="h-80 mt-4">
                                <CodeEditor
                                    language="python3"
                                    value={values?.code?.['python3']}
                                    // mdValue={nodeInfo?.outputs_md}

                                    isJSONStringifyBeauty
                                    onChange={() => {}}
                                    title={`python`}
                                ></CodeEditor>
                            </div> */}

                            <ProForm
                                initialValues={{
                                    dependencies: values?.dependencies?.['python3'] || [],
                                    output_type: values?.output_type || 1,
                                }}
                                submitter={false}
                                className="mt-4"
                                onValuesChange={(_, allValues) => {
                                    handleChange({
                                        dependencies: {
                                            python3: allValues.dependencies
                                        },
                                        output_type: allValues.output_type
                                    });
                                }}
                            >
                                <ProFormSelect
                                    label={intl.formatMessage({
                                        id: 'workflow.label.dependencies',
                                    })}
                                    mode="tags"
                                    name="dependencies"
                                    placeholder={intl.formatMessage({
                                        id: 'workflow.placeholder.enterDependencies',
                                    })}
                                    allowClear
                                    tooltip={intl.formatMessage({
                                        id: 'workflow.tooltip.dependencies',
                                    })}
                                    fieldProps={{
                                        open: false,
                                        tokenSeparators: [',', ' '],
                                    }}
                                />
                                <ProFormRadio.Group
                                    label={intl.formatMessage({ id: 'skill.result.output.type' })}
                                    name="output_type"
                                    formItemProps={{
                                        className: 'mb-0',
                                    }}
                                    fieldProps={{
                                        options: [
                                            { label: intl.formatMessage({ id: 'skill.result.output.type.text' }), value: 1 },
                                            { label: intl.formatMessage({ id: 'skill.result.output.type.database' }), value: 2 },
                                            { label: intl.formatMessage({ id: 'skill.result.output.type.code' }), value: 3 },
                                            { label: intl.formatMessage({ id: 'skill.result.output.type.document' }), value: 4 },
                                        ],
                                    }}
                                />
                            </ProForm>
                            <Variable
                                variables={Object.values(values.output_variables?.properties || {})}
                                title={intl.formatMessage({ id: 'skill.result.output.variables' })}
                                onChange={handleVariableChange('output')}
                                variableTypes={['string', 'number', 'json','file']}
                                showDescription
                            />
                        </div>

                        <div className="px-4 py-1">
                            <Paragraph
                                editable={
                                    !readOnly
                                        ? {
                                              onChange: value =>
                                                  handleChange({ obligations: value }),
                                              text: values.obligations,
                                              triggerType: ['text'],
                                              autoSize: true,
                                          }
                                        : false
                                }
                                className={`${
                                    !readOnly ? 'hover:bg-blue-100' : ''
                                } rounded-lg !mb-0 text-[12px]`}
                            >
                                {values.obligations}
                            </Paragraph>
                        </div>
                    </div>
                </Spin>
        </div>
    );
    }),
);

export default ResultDisplay;
