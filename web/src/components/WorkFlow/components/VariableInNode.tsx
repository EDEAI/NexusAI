/*
 * @LastEditors: biz
 */
import { memo } from 'react';

interface VariableInNodeProps {
    value?: Array<{ name: string }>;
}
export default memo((props: VariableInNodeProps) => {
    return (
        <>
            {props.value && props.value.length > 0 ? (
                <div className="flex flex-col gap-2 my-2">
                    {props.value.map(item => (
                        <div key={item.name} className="px-2 py-1 bg-slate-100 rounded-md">
                            {item.name}
                        </div>
                    ))}
                </div>
            ) : null}
        </>
    );
});
