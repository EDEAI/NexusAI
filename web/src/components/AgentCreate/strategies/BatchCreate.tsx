/*
 * @LastEditors: biz
 */
import { SendOutlined } from '@ant-design/icons';
import { ProFormDigit } from '@ant-design/pro-components';
import { memo } from 'react';
import BeforeCreate from '../BeforeCreate';
import { PromptTextarea } from '../ResultDisplay';

interface BatchCreateProps {
    loading: boolean;
    onSubmit: (prompt: string) => void;
    count: number;
    onCountChange: (count: number) => void;
}

const BatchCreate = memo(({ loading, onSubmit, count, onCountChange }: BatchCreateProps) => {
    return (
        <div className="flex gap-4 h-full relative">
            <BeforeCreate type="batch" hasHover={false} loading={loading} />
            <div className="flex flex-col gap-4">
                <ProFormDigit
                    label="生成数量"
                    min={1}
                    initialValue={count}
                    layout="vertical"
                    formItemProps={{
                        className: 'mb-0',
                    }}
                    fieldProps={{
                        precision: 0,
                        step: 1,
                        onChange: value => onCountChange(Number(value)),
                        controls: true,
                        parser: value => Math.floor(Number(value || 0)),
                        formatter: value => `${value}`.replace(/[^\d]/g, ''),
                    }}
                />
                <PromptTextarea
                    placeholder="输入批量生成提示词"
                    submitText="开始批量生成"
                    submitIcon={<SendOutlined />}
                    loading={loading}
                    onSubmit={onSubmit}
                    className="h-full"
                />
            </div>
        </div>
    );
});

export default BatchCreate; 