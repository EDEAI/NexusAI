/*
 * @LastEditors: biz
 */
import Headportrait from '@/components/headportrait';
import { headportrait } from '@/utils/useUser';
import { memo, useCallback } from 'react';
import { NODE_COLOR } from '../config';
import { NodeCustom } from '../nodes/nodeDisperse';
interface UserConProps {
    title: string;
    icon: string;
}
export default memo((props: UserConProps) => {
    const { title, icon } = props;
    console.log(icon);

    const RenderNodeIcon = useCallback(() => {
        if (icon?.startsWith('http:') || icon?.startsWith('https:')) {
            return (
                <div className="p-1 size-8 rounded-md flex justify-center items-center shrink-0">
                    <img src={icon} className="w-full" alt="" />
                </div>
            );
        } else if (!isNaN(Number(icon))) {
            return (
                <div className="p-1 size-8 box-border bg-gray-100  rounded-md flex justify-center items-center shrink-0">
                    <div className="size-6 flex justify-center items-center overflow-hidden">
                        <Headportrait
                            Image={headportrait('single', icon)}
                            // icon={`/icons/creation/${WORKFLOW_ICON.WorkFlow}.svg`}
                        ></Headportrait>
                    </div>
                </div>
            );
        } else if (NodeCustom[icon]) {
            return (
                <div
                    className="p-1 size-8 bg-gray-300 rounded-md flex justify-center items-center shrink-0"
                    style={{ backgroundColor: NODE_COLOR[icon] }}
                >
                    <div className="size-6 flex justify-center items-center">
                        <img src={`/icons/${icon}.svg`} className="size-6" alt={title} />
                    </div>
                </div>
            );
        }

        return (
            <div
                className="p-1 size-8 bg-gray-100 rounded-md flex justify-center items-center shrink-0"
                style={{ backgroundColor: NODE_COLOR[icon] }}
            >
                <div className="size-6 flex justify-center items-center">{icon}</div>
            </div>
        );
    }, [icon]);
    return (
        <div {...props}>
            <div className={`flex  items-center gap-2  ${title && 'py-2'}`}>
                <RenderNodeIcon />

                <div className="text-base font-medium text-gray-600">{title}</div>
            </div>
        </div>
    );
});
