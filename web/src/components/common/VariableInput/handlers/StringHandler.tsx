import React from 'react';
import { ProFormTextArea } from '@ant-design/pro-components';
import type { TypeHandlerProps } from '../types';
import { useValidationRules } from '../utils/validation';

const StringHandler: React.FC<TypeHandlerProps> = ({
  variable,
  disabled = false,
  readonly = false,
  onChange,
}) => {
  const { createStringValidationRules } = useValidationRules();
  const rules = createStringValidationRules(variable);

  return (
    <ProFormTextArea
      name={variable.name}
      label={variable.display_name || undefined}
      initialValue={variable.value}
      required={variable.required}
      disabled={disabled}
      readonly={readonly}
      rules={rules}
      fieldProps={{
        onChange: (e) => onChange?.(e.target.value),
        maxLength: variable.max_length || undefined,
        showCount: !!variable.max_length,
        rows: 4,
        placeholder: variable.required ? '请填写变量内容' : '请输入内容',
      }}
    />
  );
};

export default StringHandler; 