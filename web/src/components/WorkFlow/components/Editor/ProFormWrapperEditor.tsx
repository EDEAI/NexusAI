/*
 * @LastEditors: biz
 */
import { ProFormItem } from '@ant-design/pro-components';
import { memo, useCallback, useEffect, useState, useRef } from 'react';
import { isEqual } from 'lodash';
import WrapperEditor from './WrapperEditor';
import { MentionEditorProps } from './SlateEditorV2';

interface ProFormWrapperEditorProps {
    name: string;
    label?: string;
    tooltip?: string;
    required?: boolean;
    rules?: any[];
    title?: string;
}

const CustomWrapperEditor = memo((props: { value?: any; onChange?: (value: any) => void; title?: string; } & Omit<MentionEditorProps, 'value' | 'onChange'>) => {
    const { value, onChange, title, ...restProps } = props;
    const [internalValue, setInternalValue] = useState(value);
    const isInternalChangeRef = useRef(false);
    const lastExternalValueRef = useRef(value);

    useEffect(() => {
        // 只有当外部值真正变化且不是内部触发的变化时才更新
        if (!isInternalChangeRef.current && !isEqual(value, lastExternalValueRef.current)) {
            setInternalValue(value);
            lastExternalValueRef.current = value;
        }
        isInternalChangeRef.current = false;
    }, [value]);

    const handleChange = useCallback((newValue: any) => {
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
        <WrapperEditor
            title={title}
            value={internalValue}
            onChange={handleChange}
            {...restProps}
        />
    );
});

export default memo((props: ProFormWrapperEditorProps & Omit<MentionEditorProps, 'value' | 'onChange'>) => {
    const { name, label, tooltip, required, rules, title, ...restProps } = props;
    
    return (
        <ProFormItem
            name={name}
            label={label}
            tooltip={tooltip}
            required={required}
            rules={rules}
        >
            <CustomWrapperEditor
                title={title}
                {...restProps}
            />
        </ProFormItem>
    );
}); 