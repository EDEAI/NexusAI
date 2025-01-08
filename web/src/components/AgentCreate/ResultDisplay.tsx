import { Button, Input, Spin, Typography } from 'antd';
import React, { forwardRef, memo, useEffect, useImperativeHandle, useState } from 'react';
import TagSearch from '../TagSearch';
import { EditableCard } from './EditableCard';
import { AgentFormData } from './types';
const { Paragraph } = Typography;

export interface ResultDisplayRef {
    getValue: () => Partial<AgentFormData>;
}

interface ResultDisplayProps {
    initialValues?: Partial<AgentFormData>;
    onChange?: (values: AgentFormData) => void;
    loading?: boolean;
}

const ResultDisplay = memo(
    forwardRef<ResultDisplayRef, ResultDisplayProps>(
        ({ initialValues, onChange, loading }, ref) => {
            const [values, setValues] = useState<Partial<AgentFormData>>(initialValues || {});

            useEffect(() => {
                setValues(prev => ({
                    ...initialValues,
                    tags: prev.tags || [],
                }));
            }, [initialValues]);

            useImperativeHandle(ref, () => ({
                getValue: () => values,
            }));

            const handleChange = (updates: Partial<AgentFormData>) => {
                const newValues = { ...values, ...updates };
                setValues(newValues);
                onChange?.(newValues as AgentFormData);
            };

            return (
                <div className="flex-1 h-full pb-4 overflow-auto rounded-lg border border-gray-200 px-4 bg-gray-50 overflow-y-auto">
                    <Spin
                        spinning={loading}
                        className="h-full"
                        wrapperClassName="!h-full"
                        tip="正在生成..."
                    >
                        <div className="h-full">
                            <div className="px-4 pt-6 flex items-center gap-2">
                                <Paragraph
                                    editable={{
                                        onChange: value => handleChange({ name: value }),
                                        text: values.name,
                                        triggerType: ['text'],
                                        autoSize: true,
                                    }}
                                    className="hover:bg-blue-100 !mb-0 relative rounded-lg text-blue-600 text-[16px] flex items-center"
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
                                    editable={{
                                        onChange: value => handleChange({ description: value }),
                                        text: values.description,
                                        triggerType: ['text'],
                                        autoSize: true,
                                    }}
                                    className="hover:bg-blue-100 rounded-lg !mb-0 text-[#666666] text-[12px]"
                                >
                                    {values.description}
                                </Paragraph>
                                <div className="flex items-center hover:bg-blue-100 rounded-lg  mt-2">
                                    <img src="/icons/tag.svg" className="size-4"></img>
                                    <div className=" flex-1">
                                        <TagSearch
                                            showAddButton={false}
                                            className="w-full"
                                            variant="borderless"
                                            onChange={(tags) => {
                                                handleChange({ tags });
                                            }}
                                            value={values.tags}
                                        ></TagSearch>
                                    </div>
                                </div>
                            </div>
                            <div className="px-4 py-1">
                                <Paragraph
                                    editable={{
                                        onChange: value => handleChange({ obligations: value }),
                                        text: values.obligations,
                                        triggerType: ['text'],
                                        autoSize: true,
                                    }}
                                    className="hover:bg-blue-100 rounded-lg !mb-0 text-[12px]"
                                >
                                    {values.obligations}
                                </Paragraph>
                            </div>

                            <div className="flex flex-col gap-2 px-1 mt-2 pb-4">
                                {values.abilities?.map((item, index) => (
                                    <EditableCard
                                        key={index}
                                        title={item.name}
                                        description={item.content}
                                        outputFormat={item.output_format}
                                        onDelete={() => {
                                            const newAbilities = [...(values.abilities || [])];
                                            newAbilities.splice(index, 1);
                                            handleChange({
                                                name: values.name || '',
                                                description: values.description || '',

                                                obligations: values.obligations || '',
                                                abilities: newAbilities,
                                            });
                                        }}
                                        onChange={({ title, description, outputFormat }) => {
                                            const newAbilities = [...(values.abilities || [])];
                                            if (title !== undefined)
                                                newAbilities[index].name = title;
                                            if (description !== undefined)
                                                newAbilities[index].content = description;
                                            if (outputFormat !== undefined)
                                                newAbilities[index].output_format = outputFormat;
                                            handleChange({
                                                name: values.name || '',
                                                description: values.description || '',

                                                obligations: values.obligations || '',
                                                abilities: newAbilities,
                                            });
                                        }}
                                    />
                                ))}
                            </div>
                        </div>
                    </Spin>
                </div>
            );
        },
    ),
);

interface PromptTextareaProps {
    /** Default textarea value */
    defaultValue?: string;
    /** Callback when value changes */
    onChange?: (value: string) => void;
    /** Submit callback */
    onSubmit?: (value: string) => void;
    /** Placeholder text */
    placeholder?: string;
    /** Whether the component is disabled */
    disabled?: boolean;
    /** Loading state of submit button */
    loading?: boolean;
    /** Submit button text */
    submitText?: string;
    /** Custom class name */
    className?: string;
    /** Custom style */
    style?: React.CSSProperties;
    /** Custom button render function or ReactNode */
    renderButton?:
        | ((props: {
              disabled: boolean;
              loading: boolean;
              onClick: () => void;
              value: string;
          }) => React.ReactNode)
        | React.ReactNode;
    /** Submit button icon */
    submitIcon?: React.ReactNode;
}

export const PromptTextarea = memo(
    ({
        defaultValue = '',
        onChange,
        onSubmit,
        placeholder = 'Enter prompt',
        disabled = false,
        loading = false,
        submitText = 'Submit',
        className = '',
        style = {},
        renderButton,
        submitIcon,
    }: PromptTextareaProps) => {
        const [value, setValue] = useState(defaultValue);

        const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
            const newValue = e.target.value;
            setValue(newValue);
            onChange?.(newValue);
        };

        const handleSubmit = () => {
            if (!value.trim() || disabled || loading) return;
            onSubmit?.(value);
        };

        const renderButtonContent = () => {
            if (!renderButton) {
                return (
                    <Button
                        type="primary"
                        variant="filled"
                        color="primary"
                        loading={loading}
                        disabled={!value.trim() || disabled}
                        onClick={handleSubmit}
                        icon={submitIcon}
                    >
                        {submitText}
                    </Button>
                );
            }

            if (typeof renderButton === 'function') {
                return renderButton({
                    disabled: !value.trim() || disabled,
                    loading,
                    onClick: handleSubmit,
                    value,
                });
            }

            return React.cloneElement(renderButton as React.ReactElement, {
                onClick: handleSubmit,
                disabled: !value.trim() || disabled,
                loading,
            });
        };

        return (
            <div className={`relative ${className}`} style={style}>
                <Input.TextArea
                    defaultValue={defaultValue}
                    onChange={handleChange}
                    placeholder={placeholder}
                    disabled={disabled}
                    className="w-full !h-full p-3 pr-9 rounded-lg border border-gray-200 resize-none outline-none focus:border-blue-500 transition-colors"
                />
                <div className="absolute right-2 bottom-2">{renderButtonContent()}</div>
            </div>
        );
    },
);
export default ResultDisplay;
