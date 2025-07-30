export type VariableType = 'string' | 'number' | 'file' | 'json';

export interface Variable {
  name: string;
  type: VariableType;
  value?: any;
  display_name?: string;
  required?: boolean;
  max_length?: number;
  sort_order?: number;
}

export interface FileConfig {
  accept?: string;
  maxSize?: number;
  multiple?: boolean;
}

export interface VariableInputProps {
  // Core properties
  variable: Variable;
  
  // Optional configurations
  disabled?: boolean;
  readonly?: boolean;
  
  // Callback functions
  onChange?: (value: any) => void;
  onValidationChange?: (isValid: boolean) => void;
  
  // Type-specific configurations
  fileConfig?: FileConfig;
  
  // Style configurations
  className?: string;
  style?: React.CSSProperties;
}

export interface TypeHandlerProps {
  variable: Variable;
  disabled?: boolean;
  readonly?: boolean;
  onChange?: (value: any) => void;
  fileConfig?: FileConfig;
}

export interface ValidationRule {
  required?: boolean;
  message: string;
  validator?: (rule: any, value: any) => Promise<void>;
} 