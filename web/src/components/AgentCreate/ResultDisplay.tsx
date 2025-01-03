import { ProForm, ProFormList, ProFormSelect, ProFormText, ProFormTextArea } from '@ant-design/pro-components';
import { Form } from 'antd';
import { memo } from 'react';
import { AgentFormData, AgentSkill } from './types';

interface ResultDisplayProps {
    initialValues?: Partial<AgentFormData>;
    onChange?: (values: AgentFormData) => void;
    loading?: boolean;
}

const ResultDisplay = memo(({ initialValues, onChange, loading }: ResultDisplayProps) => {
    const [form] = Form.useForm();

    return (
        <div className="flex-1 h-full rounded-lg border border-gray-200 p-4 bg-gray-50 overflow-y-auto">
            <ProForm
                form={form}
                submitter={false}
                initialValues={initialValues}
                onValuesChange={(_, values) => onChange?.(values as AgentFormData)}
                disabled={loading}
            >
                <div className="h-full overflow-auto">
                    <ProFormText
                        label="名称"
                        name="name"
                        rules={[{ required: true, message: '请输入名称' }]}
                    />
                    <ProFormTextArea
                        label="描述"
                        name="description"
                        rules={[{ required: true, message: '请输入描述' }]}
                    />
                    <ProFormTextArea
                        label="职能描述"
                        name="prompt"
                        rules={[{ required: true, message: '请输入职能描述' }]}
                    />
                    <ProFormList
                        name="skill_list"
                        label="技能"
                        creatorButtonProps={{
                            creatorButtonText: '添加技能',
                        }}
                        min={1}
                        copyIconProps={false}
                        containerClassName="w-full pb-4"
                    >
                        <div className="p-4 bg-white rounded-lg border border-gray-200">
                            <ProFormText
                                label="名称"
                                name="skill"
                                rules={[{ required: true, message: '请输入技能名称' }]}
                                formItemProps={{
                                    className: 'mb-3',
                                }}
                            />
                            <ProFormTextArea
                                label="描述"
                                name="description"
                                rules={[{ required: true, message: '请输入技能描述' }]}
                                formItemProps={{
                                    className: 'mb-3',
                                }}
                            />
                            <ProFormSelect
                                label="输出格式"
                                name="output_format"
                                rules={[{ required: true, message: '请选择输出格式' }]}
                                options={[
                                    { label: 'JSON', value: 'json' },
                                ]}
                                formItemProps={{
                                    className: 'mb-0',
                                }}
                            />
                        </div>
                    </ProFormList>
                </div>
            </ProForm>
        </div>
    );
});

export default ResultDisplay; 