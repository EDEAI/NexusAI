/*
 * @LastEditors: biz
 */
import { memo } from 'react';

interface BeforeCreateProps {
    type?: 'single' | 'batch';
    loading?: boolean;
    onClick?: () => void;
    hasHover?: boolean;
}

const BeforeCreate = memo(({ type = 'single', loading = false, onClick, hasHover = true }: BeforeCreateProps) => {
    return (
        <div 
            onClick={onClick} 
            className={`
                flex-1 h-full pb-4 rounded-lg border border-gray-200 px-4 bg-gray-50 overflow-y-auto
                ${hasHover ? 'cursor-pointer hover:border-blue-500 hover:bg-blue-100' : ''}
            `}
        >
            <div className="flex justify-center items-center flex-col w-full h-full">
                <img 
                    src={type === 'single' ? '/icons/agent_create.svg' : '/icons/agents_create.svg'} 
                    className="size-16" 
                />
                <div className="mt-2">
                    {type === 'single' ? '生成智能体' : '批量生成智能体'}
                </div>
                {loading && <div className="mt-2 text-gray-400">生成中...</div>}
            </div>
        </div>
    );
});

export default BeforeCreate; 