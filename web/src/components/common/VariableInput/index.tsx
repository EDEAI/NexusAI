/*
 * @LastEditors: biz
 */
import React, { memo, useCallback } from 'react';
import type { VariableInputProps } from './types';
import { useTypeDetection } from './hooks/useTypeDetection';

const VariableInput: React.FC<VariableInputProps> = ({
  variable,
  disabled = false,
  readonly = false,
  onChange,
  onValidationChange,
  fileConfig,
  className,
  style,
}) => {
  const { getHandlerComponent, normalizeVariable } = useTypeDetection(variable);
  const normalizedVariable = normalizeVariable(variable);
  const HandlerComponent = getHandlerComponent;

  const handleChange = useCallback((value: any) => {
    onChange?.(value);
  }, [onChange]);

  const handlerProps = {
    variable: normalizedVariable,
    disabled,
    readonly,
    onChange: handleChange,
    fileConfig,
  };

  return (
    <div className={className} style={style}>
      <HandlerComponent {...handlerProps} />
    </div>
  );
};

export default memo(VariableInput);
export type { VariableInputProps, Variable, VariableType, FileConfig } from './types'; 