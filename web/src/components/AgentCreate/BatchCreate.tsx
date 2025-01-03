/*
 * @LastEditors: biz
 */
import { ProForm, ProFormDigit, ProFormTextArea } from '@ant-design/pro-components';
import { Form, Modal } from 'antd';
import { memo, useCallback } from 'react';
import { BatchCreateFormData } from './types';

interface BatchCreateProps {
    open: boolean;
    onCancel: () => void;
    onOk: (data: BatchCreateFormData) => void;
    loading?: boolean;
}

const BatchCreate = memo(({ open, onCancel, onOk, loading }: BatchCreateProps) => {
    const [form] = Form.useForm();

    const handleOk = async () => {
        const values = await form.validateFields();
        const prompts = values.prompts
            .split('\n')
            .map(p => p.trim())
            .filter(Boolean);

        onOk({
            count: values.count,
            prompts: prompts.join('\n'),
            additionalPrompt: values.additionalPrompt,
        });
    };

    const RenderCreateInput = () => {
        return (
            <div className="flex-1">
                <ProForm form={form} submitter={false} disabled={loading}>
                    <ProFormDigit
                        name="count"
                        label="生成数量"
                        min={1}
                        max={10}
                        initialValue={1}
                        fieldProps={{
                            precision: 0,
                        }}
                        rules={[{ required: true, message: '请输入生成数量' }]}
                    />
                    <ProFormTextArea
                        name="prompts"
                        label="智能体提示词"
                        placeholder="请输入补充性的提示词，将会添加到每个智能体的生成提示中"
                        rules={[{ required: true, message: '请输入提示词' }]}
                        fieldProps={{
                            rows: 8,
                            autoSize: { minRows: 8, maxRows: 15 },
                        }}
                    />
                </ProForm>
            </div>
        );
    };

    const BatchIcon = () => (
        <div className="relative w-20 h-20">
            <img 
                src="/icons/plaza_m2_c1.svg" 
                className="absolute size-16 opacity-30 -right-4 -top-2"
            />
            <img 
                src="/icons/plaza_m2_c1.svg" 
                className="absolute size-16 opacity-60 -right-2 -top-1"
            />
            <img 
                src="/icons/plaza_m2_c1.svg" 
                className="absolute size-16 right-0 top-0"
            />
        </div>
    );

    const BeforeCreate = useCallback(
        () => (
            <div className="rounded-lg flex-1 border border-gray-200 p-4 bg-gray-50 flex justify-center items-center flex-col gap-2 text-[#1b64f3]">
                <BatchIcon />
                {loading ? <div>生成中...</div> : <div>待生成智能体</div>}
            </div>
        ),
        [loading],
    );

    return (
        <Modal
            title="批量生成智能体"
            className="min-w-[1000px]"
            bodyProps={{
                className: '!h-[600px] overflow-y-auto p-4',
            }}
            open={open}
            onCancel={onCancel}
            onOk={handleOk}
            confirmLoading={loading}
        >
            <div className="flex gap-4 h-full">
                <BeforeCreate />
                <RenderCreateInput />
            </div>
        </Modal>
    );
});

export default BatchCreate;
