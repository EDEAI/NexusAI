/*
 * @LastEditors: biz
 */
import Headportrait from '@/components/headportrait';
import { headportrait } from '@/utils/useUser';
import { memo, useCallback } from 'react';
import { NODE_COLOR } from '../config';
import { NodeCustom } from '../nodes/nodeDisperse';

export interface UserConProps {
    title: string;
    desc?: string;
    icon: string;
    extra?: React.ReactNode;
    className?: string;
    typeBadge?: {
        icon: string;
        tooltip?: string;
        color?: string;
    };
}

// 类型图标组件
const TypeBadge = memo(({ icon, tooltip, color = 'white' }: NonNullable<UserConProps['typeBadge']>) => (
    <div 
        className="absolute bottom-[-3px] right-[-3px] w-4 h-4 hover:scale-150 rounded-full flex items-center justify-center shadow-[0_0_4px_-0_rgba(0,0,0,0.2)]"
        style={{ backgroundColor: color }}
        title={tooltip}
    >
        <img 
            src={icon}
            className="size-3 text-lime-500" 
            alt={tooltip}
        />
    </div>
));

// 图标渲染组件
const IconRenderer = memo(({ icon, title, typeBadge }: Pick<UserConProps, 'icon' | 'title' | 'typeBadge'>) => {
    const baseClasses = "p-1 size-8 rounded-md flex justify-center items-center shrink-0 relative";
    const innerClasses = "size-6 flex justify-center items-center";

    const renderIcon = () => {
        if (icon?.startsWith('http:') || icon?.startsWith('https:')) {
            return (
                <div className={`${baseClasses} !p-0`}>
                    <img src={icon} className="w-full rounded" alt={title} />
                    {typeBadge && <TypeBadge {...typeBadge} />}
                </div>
            );
        }
        
        if (!isNaN(Number(icon))) {
            return (
                <div className={`${baseClasses} bg-gray-100 box-border`}>
                    <div className={`${innerClasses} overflow-hidden`}>
                        <Headportrait Image={headportrait('single', icon)} />
                    </div>
                    {typeBadge && <TypeBadge {...typeBadge} />}
                </div>
            );
        }
        
        if (NodeCustom[icon]) {
            return (
                <div 
                    className={`${baseClasses} bg-gray-300`}
                    style={{ backgroundColor: NODE_COLOR[icon] }}
                >
                    <div className={innerClasses}>
                        <img src={`/icons/${icon}.svg`} className="size-6" alt={title} />
                    </div>
                    {typeBadge && <TypeBadge {...typeBadge} />}
                </div>
            );
        }

        return (
            <div 
                className={`${baseClasses} bg-gray-100`}
                style={{ backgroundColor: NODE_COLOR[icon] }}
            >
                <div className={innerClasses}>{icon}</div>
                {typeBadge && <TypeBadge {...typeBadge} />}
            </div>
        );
    };

    return renderIcon();
});

export default memo(({ title, desc, icon, extra, className = '', typeBadge, ...props }: UserConProps) => {
    return (
        <div {...props} className={className}>
            <div className={`flex items-center gap-2 ${title ? 'py-2' : ''}`}>
                <IconRenderer icon={icon} title={title} typeBadge={typeBadge} />
                <div className="flex flex-col">
                    <div className="text-base font-medium text-gray-600">{title}</div>
                    {desc && <div className="text-sm text-gray-400">{desc}</div>}
                </div>
                {extra && <div className="ml-auto">{extra}</div>}
            </div>
        </div>
    );
});
