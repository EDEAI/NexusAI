/*
 * @LastEditors: biz
 */
import { SendOutlined, ToolOutlined } from '@ant-design/icons';
import { memo } from 'react';
import BeforeCreate from '../BeforeCreate';
import { PromptTextarea } from '../ResultDisplay';

interface SingleCreateProps {
    loading: boolean;
    onSubmit: (prompt: string) => void;
    correctLoading?: boolean;
    onCorrect?: (prompt: string) => void;
    showCorrect?: boolean;
}

const SingleCreate = memo(({ loading, onSubmit, correctLoading, onCorrect, showCorrect }: SingleCreateProps) => {
    return (
        <div className="flex gap-4 h-full relative">
            <BeforeCreate type="single" hasHover={false} loading={loading} />
            <div className="flex flex-col gap-4 relative">
                <PromptTextarea
                    placeholder="输入智能体生成提示词"
                    submitText="生成智能体"
                    submitIcon={<SendOutlined />}
                    loading={loading}
                    onSubmit={onSubmit}
                    className="h-full"
                />
                {showCorrect && (
                    <PromptTextarea
                        placeholder="输入智能体生成提示词"
                        submitText="修正智能体"
                        submitIcon={<ToolOutlined />}
                        loading={correctLoading}
                        onSubmit={onCorrect}
                        className="h-full"
                    />
                )}
            </div>
        </div>
    );
});

export default SingleCreate; 