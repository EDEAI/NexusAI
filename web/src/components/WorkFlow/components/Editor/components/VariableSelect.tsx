/*
 * @LastEditors: biz
 */
import React, { forwardRef } from 'react';

interface VariableSelectProps {
    style: React.CSSProperties;
    list?: any[];
    onChange?: (item: any, index: number) => void;
}

const VariableSelect = forwardRef<HTMLDivElement, VariableSelectProps>((props, ref) => {
    const { style, list = [], onChange, ...rest } = props;

    return (
        <div ref={ref} style={{ ...style, zIndex: 99 }} {...rest}>
            <div className="py-2 bg-white border rounded-md shadow-md w-36">
                {list.map((item, index) => (
                    <div
                        key={index}
                        onClick={() => {
                            onChange && onChange(item, index);
                        }}
                        className="cursor-pointer hover:bg-gray-100 p-2"
                    >
                        {item.name}
                    </div>
                ))}
            </div>
        </div>
    );
});

export default VariableSelect;
