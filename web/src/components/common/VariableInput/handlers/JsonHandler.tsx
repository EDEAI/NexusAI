import React from 'react';
import { ProFormTextArea } from '@ant-design/pro-components';
import type { TypeHandlerProps } from '../types';
import { useValidationRules } from '../utils/validation';

const JsonHandler: React.FC<TypeHandlerProps> = ({
  variable,
  disabled = false,
  readonly = false,
  onChange,
}) => {
  const { createJsonValidationRules } = useValidationRules();
  const rules = createJsonValidationRules(variable);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    onChange?.(value);
  };

  const formatValue = () => {
    if (variable.value && typeof variable.value === 'object') {
      return JSON.stringify(variable.value, null, 2);
    }
    return variable.value || '';
  };

  return (
    <ProFormTextArea
      name={variable.name}
      label={variable.display_name || undefined}
      initialValue={formatValue()}
      required={variable.required}
      disabled={disabled}
      readonly={readonly}
      rules={rules}
      fieldProps={{
        onChange: handleChange,
        rows: 6,
        placeholder: variable.required ? '请填写JSON格式内容' : '{\n  "key": "value"\n}',
        style: { fontFamily: 'monospace' },
      }}
      tooltip="Please enter valid JSON format"
    />
  );
};

export default JsonHandler; 