import React from 'react';
import { ProFormDigit } from '@ant-design/pro-components';
import type { TypeHandlerProps } from '../types';
import { useValidationRules } from '../utils/validation';

const NumberHandler: React.FC<TypeHandlerProps> = ({
  variable,
  disabled = false,
  readonly = false,
  onChange,
}) => {
  const { createNumberValidationRules } = useValidationRules();
  const rules = createNumberValidationRules(variable);

  return (
    <ProFormDigit
      name={variable.name}
      label={variable.display_name || undefined}
      initialValue={variable.value}
      required={variable.required}
      disabled={disabled}
      readonly={readonly}
      rules={rules}
      fieldProps={{
        onChange: (value) => onChange?.(value),
        precision: 2,
        placeholder: variable.required ? '请填写数字' : '请输入数字',
      }}
    />
  );
};

export default NumberHandler; 