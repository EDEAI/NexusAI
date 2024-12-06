/*
 * @LastEditors: biz
 */
import { memo } from 'react';
interface UserConProps {
    title: string;
    icon: string;
}
export default memo((props: UserConProps) => {
    const { title, icon } = props;

    return (
        <div {...props}>
            <div className={`flex  items-center gap-2  ${title && 'py-2'}`}>
                {icon.startsWith('http:') || icon.startsWith('https:') ? (
                    <div className="p-1 size-8 rounded-md flex justify-center items-center shrink-0">
                        <img src={icon} className="w-full" alt="" />
                    </div>
                ) : (
                    <div className="p-1 size-8 bg-gray-300 rounded-md flex justify-center items-center shrink-0">
                        <img src={`/icons/${icon}.svg`} className="size-6" alt={title} />
                    </div>
                )}

                <div className="text-base font-medium text-gray-600">{title}</div>
            </div>
        </div>
    );
});
