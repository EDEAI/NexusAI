import { useMemo } from 'react';
import type { Variable, VariableType } from '../types';
import StringHandler from '../handlers/StringHandler';
import NumberHandler from '../handlers/NumberHandler';
import FileHandler from '../handlers/FileHandler';
import JsonHandler from '../handlers/JsonHandler';

export const useTypeDetection = (variable: Variable) => {
  const getHandlerComponent = useMemo(() => {
    switch (variable.type) {
      case 'number':
        return NumberHandler;
      case 'file':
        return FileHandler;
      case 'json':
        return JsonHandler;
      case 'string':
      default:
        return StringHandler;
    }
  }, [variable.type]);

  const validateType = (type: string): type is VariableType => {
    return ['string', 'number', 'file', 'json'].includes(type);
  };

  const normalizeVariable = (inputVariable: Variable): Variable => {
    // Ensure type is valid, default to 'string' if invalid
    const normalizedType = validateType(inputVariable.type) ? inputVariable.type : 'string';
    
    return {
      ...inputVariable,
      type: normalizedType,
      required: inputVariable.required ?? false,
      sort_order: inputVariable.sort_order ?? 0,
    };
  };

  return {
    getHandlerComponent,
    validateType,
    normalizeVariable,
  };
}; 