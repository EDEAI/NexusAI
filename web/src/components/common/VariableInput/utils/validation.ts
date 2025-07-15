import { useIntl } from '@umijs/max';
import type { Variable, ValidationRule } from '../types';

export const useValidationRules = () => {
  const intl = useIntl();

  const createRequiredRule = (required: boolean): ValidationRule | null => {
    if (!required) return null;
    
    return {
      required: true,
      message: intl.formatMessage({
        id: 'skill.message.variantcontent',
        defaultMessage: '请填写变量内容',
      }),
    };
  };

  const createStringValidationRules = (variable: Variable): ValidationRule[] => {
    const rules: ValidationRule[] = [];
    
    const requiredRule = createRequiredRule(variable.required || false);
    if (requiredRule) rules.push(requiredRule);
    
    if (variable.max_length && variable.max_length > 0) {
      rules.push({
        message: intl.formatMessage({
          id: 'workflow.form.parameter.maxLength',
          defaultMessage: `Maximum length is ${variable.max_length} characters`,
        }),
        validator: async (_, value) => {
          if (value && value.length > variable.max_length!) {
            throw new Error();
          }
        },
      });
    }
    
    return rules;
  };

  const createNumberValidationRules = (variable: Variable): ValidationRule[] => {
    const rules: ValidationRule[] = [];
    
    const requiredRule = createRequiredRule(variable.required || false);
    if (requiredRule) rules.push(requiredRule);
    
    return rules;
  };

  const createFileValidationRules = (variable: Variable): ValidationRule[] => {
    const rules: ValidationRule[] = [];
    
    const requiredRule = createRequiredRule(variable.required || false);
    if (requiredRule) rules.push(requiredRule);
    
    return rules;
  };

  const createJsonValidationRules = (variable: Variable): ValidationRule[] => {
    const rules: ValidationRule[] = [];
    
    const requiredRule = createRequiredRule(variable.required || false);
    if (requiredRule) rules.push(requiredRule);
    
    rules.push({
      message: intl.formatMessage({
        id: 'workflow.form.parameter.invalidJson',
        defaultMessage: 'Please enter valid JSON format',
      }),
      validator: async (_, value) => {
        if (value && value.trim()) {
          try {
            JSON.parse(value);
          } catch (error) {
            throw new Error();
          }
        }
      },
    });
    
    return rules;
  };

  return {
    createStringValidationRules,
    createNumberValidationRules,
    createFileValidationRules,
    createJsonValidationRules,
  };
}; 