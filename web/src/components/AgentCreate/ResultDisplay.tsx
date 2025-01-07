import { Button, Input, Typography } from 'antd';
import React, { memo, useState } from 'react';
import TagSearch from '../TagSearch';
import { EditableCard } from './EditableCard';
import { AgentFormData } from './types';
const { Paragraph } = Typography;
interface ResultDisplayProps {
    initialValues?: Partial<AgentFormData>;
    onChange?: (values: AgentFormData) => void;
    loading?: boolean;
}

const ResultDisplay = memo(({ initialValues, onChange, loading }: ResultDisplayProps) => {
    const [editableStrWithSuffix, setEditableStrWithSuffix] = useState(
        initialValues?.description || '',
    );
    console.log(initialValues);
    
    return (
        <div className="flex-1 h-full pb-4 overflow-auto rounded-lg border border-gray-200 px-4 bg-gray-50 overflow-y-auto">
            <div className="h-full">
                <div className="px-4 pt-6 flex items-center gap-2">
                    <Paragraph
                        editable={{
                            onChange: setEditableStrWithSuffix,
                            text: initialValues?.name,
                            triggerType: ['text'],
                            autoSize: true,
                        }}
                        className="hover:bg-blue-100 !mb-0 relative rounded-lg text-blue-600 text-[16px] flex items-center"
                    >
                        <img src="/icons/agent_create.svg" className="size-6 mr-1"></img>
                        {initialValues?.name}
                    </Paragraph>
                </div>
                <div className="px-4 py-1 mt-2">
                    <Paragraph
                        editable={{
                            onChange: setEditableStrWithSuffix,
                            text: initialValues?.description,
                            triggerType: ['text'],
                            autoSize: true,
                        }}
                        className=" hover:bg-blue-100 rounded-lg !mb-0 text-[#666666] text-[12px]"
                        rootClassName=""
                    >
                        {initialValues?.description}
                    </Paragraph>
                    <div className="flex items-center hover:bg-blue-100 rounded-lg  mt-2">
                        <img src="/icons/tag.svg" className="size-4"></img>
                        <div className=" flex-1">
                            <TagSearch
                                showAddButton={false}
                                className="w-full"
                                variant="borderless"
                            ></TagSearch>
                        </div>
                    </div>
                </div>
                <div className="px-4 py-1">
                    <Paragraph
                        editable={{
                            onChange: setEditableStrWithSuffix,
                            text: initialValues?.obligations,
                            triggerType: ['text'],
                            autoSize: true,
                        }}
                        className=" hover:bg-blue-100 rounded-lg !mb-0  text-[12px]"
                    >
                        {initialValues?.obligations}
                    </Paragraph>
                </div>

                <div className="flex flex-col gap-2 px-1 mt-2 pb-4">
                    {initialValues?.abilities?.map((item, index) => (
                        <EditableCard
                            key={index}
                            title={item.name}
                            description={item.content}
                            outputFormat={item.output_format}
                            onDelete={() => {
                                const newSkillList = [...initialValues.skill_list];
                                newSkillList.splice(index, 1);
                                onChange?.({
                                    name: initialValues.name || '',
                                    description: initialValues.description || '',
                                    prompt: initialValues.prompt || '',
                                    obligations: initialValues.obligations || '',
                                    abilities: initialValues.abilities || [],
                                    skill_list: newSkillList,
                                });
                            }}
                            onChange={({ title, description, outputFormat }) => {
                                const newSkillList = [...initialValues.skill_list];
                                if (title !== undefined) newSkillList[index].skill = title;
                                if (description !== undefined)
                                    newSkillList[index].description = description;
                                if (outputFormat !== undefined)
                                    newSkillList[index].output_format =
                                        outputFormat === 2 ? 'json' : 'text';
                                onChange?.({
                                    name: initialValues.name || '',
                                    description: initialValues.description || '',
                                    prompt: initialValues.prompt || '',
                                    obligations: initialValues.obligations || '',
                                    abilities: initialValues.abilities || [],
                                    skill_list: newSkillList,
                                });
                            }}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
});

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
