/*
 * @LastEditors: biz
 */
import { ProFormItem } from '@ant-design/pro-components';
import { memo, useCallback, useEffect, useState, useRef } from 'react';
import { isEqual } from 'lodash';
import { getCharacterCount } from './components/slateEditorUtils';
import SlateEditorV3, { type Variable, type MentionOption } from './SlateEditorV3';
import type { Descendant } from 'slate';

// 更新接口定义以匹配 V3
export interface MentionEditorProps {
    value?: Descendant[];
    onChange?: (value: Descendant[]) => void;
    id?: string;
    placeholder?: string;
    options?: MentionOption[];
    variables?: Variable[];
}

interface ProFormWrapperEditorProps {
    name: string;
    label?: string;
    tooltip?: string;
    required?: boolean;
    rules?: any[];
    title?: string;
}

interface WrapperEditorProps {
    title?: string;
}

// V3 版本的 WrapperEditor
const WrapperEditorV3 = memo<WrapperEditorProps & MentionEditorProps>(({ 
    title, 
    onChange, 
    ...restProps 
}) => {
    const [len, setLen] = useState(0);
    
    const handleChange = (value: Descendant[]) => {
        onChange?.(value);
        setLen(getCharacterCount(value || []));
    };
    
    return (
        <div className="p-2 border-stone-300 border rounded-md my-2">
            <div className="flex justify-between cursor-default">
                <div>
                    {title && <div className="text-sm text-gray-500 font-bold pb-2">{title}</div>}
                </div>
                <div className="text-blue-400">{len}</div>
            </div>
            <div className="max-h-48 min-h-24 overflow-y-auto">
                <SlateEditorV3 onChange={handleChange} {...restProps} />
            </div>
        </div>
    );
});

const CustomWrapperEditorV3 = memo<{ 
    value?: Descendant[]; 
    onChange?: (value: Descendant[]) => void; 
    title?: string; 
} & Omit<MentionEditorProps, 'value' | 'onChange'>>((props) => {
    const { value, onChange, title, ...restProps } = props;
    const [internalValue, setInternalValue] = useState<Descendant[]>(value || []);
    const isInternalChangeRef = useRef(false);
    const lastExternalValueRef = useRef(value);

    useEffect(() => {
        // 只有当外部值真正变化且不是内部触发的变化时才更新
        if (!isInternalChangeRef.current && !isEqual(value, lastExternalValueRef.current)) {
            setInternalValue(value || []);
            lastExternalValueRef.current = value;
        }
        isInternalChangeRef.current = false;
    }, [value]);

    const handleChange = useCallback((newValue: Descendant[]) => {
        // 避免相同值的重复更新
        if (isEqual(newValue, internalValue)) {
            return;
        }
        
        isInternalChangeRef.current = true;
        setInternalValue(newValue);
        lastExternalValueRef.current = newValue;
        onChange?.(newValue);
    }, [onChange, internalValue]);

    return (
        <WrapperEditorV3
            title={title}
            value={internalValue}
            onChange={handleChange}
            {...restProps}
        />
    );
});

const ProFormWrapperEditorV3 = memo<ProFormWrapperEditorProps & Omit<MentionEditorProps, 'value' | 'onChange'>>((props) => {
    const { name, label, tooltip, required, rules, title, ...restProps } = props;
    
    return (
        <ProFormItem
            name={name}
            label={label}
            tooltip={tooltip}
            required={required}
            rules={rules}
        >
            <CustomWrapperEditorV3
                title={title}
                {...restProps}
            />
        </ProFormItem>
    );
});

export default ProFormWrapperEditorV3; 