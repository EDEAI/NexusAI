/*
 * @LastEditors: biz
 */
import { memo } from 'react';
import { useIntl } from '@umijs/max';

interface BeforeCreateProps {
    type?: 'single' | 'batch';
    loading?: boolean;
    onClick?: () => void;
    hasHover?: boolean;
}

const BeforeCreate = memo(({ type = 'single', loading = false, onClick, hasHover = true }: BeforeCreateProps) => {
    const intl = useIntl();

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
                <div className="text-lg font-medium mt-4">
                    {type === 'single' 
                        ? intl.formatMessage({ id: 'agent.before.single.desc' })
                        : intl.formatMessage({ id: 'agent.before.batch.desc' })
                    }
                </div>
                {loading && (
                    <div className="mt-2 text-gray-400">
                        {intl.formatMessage({ id: 'agent.before.loading' })}
                    </div>
                )}
            </div>
        </div>
    );
});

export default BeforeCreate; 