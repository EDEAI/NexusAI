/*
 * @LastEditors: biz
 */
import { ProFormSwitch, ProFormSwitchProps } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';

const switchConfigs = {
    requires_upload: {
        name: 'requires_upload',
        label: '',
        tooltip: '，“”，',
    },
    import_to_knowledge_base: {
        name: 'import_to_knowledge_base',
        label: '',
        tooltip: '，',
    },
    manual_confirmation: {
        name: 'manual_confirmation',
        label: '',
        tooltip: '',
    },
    wait_for_all_predecessors: {
        name: 'wait_for_all_predecessors',
        label: '',
        tooltip: '',
    },
    split_task_by_line: {
        name: 'split_task_by_line',
        label: '',
        tooltip: '',
    },
} as const;

type FieldName = keyof typeof switchConfigs;
const typedSwitchConfigs: Record<FieldName, ProFormSwitchProps> = switchConfigs;

interface SwitchGroupProps {
    fields: FieldName[];
    onChange?: (value: boolean) => void;
}

export const SwitchGroup: React.FC<SwitchGroupProps> = ({ fields, onChange }) => {
    const intl = useIntl();
    return (
        <div className="user-form mt-6">
            {fields.map(field =>
                typedSwitchConfigs[field] ? (
                    <ProFormSwitch
                        key={field}
                        {...typedSwitchConfigs[field]}
                        label={intl.formatMessage({
                            id: `workflow.${field}`,
                        })}
                        tooltip={intl.formatMessage({
                            id: `workflow.${field}Des`,
                        })}
                        fieldProps={
                            {
                                onChange: checked => {
                                    onChange?.(checked);
                                },
                            }
                        }
                      
                    ></ProFormSwitch>
                ) : null,
            )}
        </div>
    );
};

/**
 * Render the switch for allowing file upload
 * @returns {JSX.Element} ProFormSwitch component
 */
export const SwitchRequiresUpload = () => {
    return <SwitchGroup fields={['requires_upload']} />;
};

/**
 * Render the switch for importing to the knowledge base
 * @returns {JSX.Element} ProFormSwitch component
 */
export const SwitchImportToKnowledgeBase = () => {
    return <SwitchGroup fields={['import_to_knowledge_base']} />;
};

/**
 * Render the switch for manual confirmation
 * @returns {JSX.Element} ProFormSwitch component
 */
export const SwitchManualConfirmation = () => {
    return <SwitchGroup fields={['manual_confirmation']} />;
};
/**
 * Render the switch for splitting tasks by line
 * @returns {JSX.Element} ProFormSwitch component
 */
export const SwitchSplitTaskByLine = ({ onChange }: { onChange?: (value: boolean) => void }) => {
    return <SwitchGroup fields={['split_task_by_line']} onChange={onChange} />;
};


/**
 * Render the switch for waiting for all predecessor nodes
 * @returns {JSX.Element} ProFormSwitch component
 */
export const SwitchWaitForAllPredecessors = () => {
    return null;
    return <SwitchGroup fields={['wait_for_all_predecessors']} />;
};
