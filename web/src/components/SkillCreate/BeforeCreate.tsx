

/*
 * @LastEditors: biz
 */
import { useIntl } from '@umijs/max';
import { Spin } from 'antd';
import { memo } from 'react';

interface BeforeCreateProps {
    loading?: boolean;
    onClick?: () => void;
    hasHover?: boolean;
    icon?: string | React.ReactNode;
    title?: string;
    description?: string;
    loadingText?: string;
}

const BeforeCreate = memo(({ 
    loading = false, 
    onClick, 
    hasHover = true,
    icon = '/icons/agent_skill.svg',
    title,
    description,
    loadingText
}: BeforeCreateProps) => {
    const intl = useIntl();

    const renderIcon = () => {
        if (typeof icon === 'string') {
            return <img src={icon} className="size-16" />;
        }
        return icon;
    };

    return (
        <div
            onClick={onClick}
            className={`
                flex-1 h-full pb-4 rounded-lg border border-gray-200 px-4 bg-gray-50 overflow-y-auto
                ${hasHover ? 'cursor-pointer hover:border-blue-500 hover:bg-blue-100' : ''}
            `}
        >
           
                <div className="flex flex-col items-center justify-center h-full">
                    {renderIcon()}
                    <div className="text-lg font-medium mt-4">{title}</div>
                    <div className="text-gray-500 mt-2">{description}</div>
                    {loading && (
                    <div className="mt-2 text-gray-400">
                        {loadingText || intl.formatMessage({ id: 'skill.before.loading' })}
                    </div>
                )}
                </div>
           
        </div>
    );
});

export default BeforeCreate;
