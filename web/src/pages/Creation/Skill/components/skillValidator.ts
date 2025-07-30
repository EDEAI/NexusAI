/**
 * Skill data validation utility module
 * Provides unified data validation functionality, independent of UI components
 */

import _ from 'lodash';

export interface ValidationError {
    field: string;
    message: string;
    type: 'error' | 'warning';
    code: string;
}

export interface ValidationResult {
    isValid: boolean;
    errors: ValidationError[];
}

export interface SkillData {
    name?: string;
    description?: string;
    input_variables?: any;
    output_variables?: any;
    code?: string;
}

/**
 * Find duplicate elements in an array
 */
const findDuplicates = (arr: string[]): string[] => {
    return arr.filter((item, index) => arr.indexOf(item) !== index);
};

/**
 * Validate input variables
 */
export const validateInputVariables = (input_variables: any): ValidationResult => {
    const errors: ValidationError[] = [];

    // Check if input variables exist
    if (!input_variables) {
        errors.push({
            field: 'input_variables',
            message: 'Input variables cannot be empty',
            type: 'error',
            code: 'INPUT_VARIABLES_REQUIRED'
        });
        return { isValid: false, errors };
    }

    // Check if properties exist and are not empty
    if (!input_variables.properties || _.isEmpty(input_variables.properties)) {
        errors.push({
            field: 'input_variables.properties',
            message: 'At least one input variable must be defined',
            type: 'error',
            code: 'INPUT_VARIABLES_EMPTY'
        });
        return { isValid: false, errors };
    }

    // Check for duplicate variable names
    const variableNames = Object.keys(input_variables.properties);
    const duplicateNames = findDuplicates(variableNames);
    if (duplicateNames.length > 0) {
        errors.push({
            field: 'input_variables.properties',
            message: `Duplicate variable names: ${duplicateNames.join(', ')}`,
            type: 'error',
            code: 'INPUT_VARIABLES_DUPLICATE'
        });
    }

    // Validate basic information for each variable
    Object.entries(input_variables.properties).forEach(([key, variable]: [string, any]) => {
        if (!variable.name || variable.name.trim() === '') {
            errors.push({
                field: `input_variables.properties.${key}.name`,
                message: `Variable ${key} name cannot be empty`,
                type: 'error',
                code: 'VARIABLE_NAME_REQUIRED'
            });
        }

        if (!variable.display_name || variable.display_name.trim() === '') {
            errors.push({
                field: `input_variables.properties.${key}.display_name`,
                message: `Variable ${key} display name cannot be empty`,
                type: 'error',
                code: 'VARIABLE_DISPLAY_NAME_REQUIRED'
            });
        }

        // Validate variable name format
        if (variable.name && !/^[a-zA-Z0-9_]+$/.test(variable.name)) {
            errors.push({
                field: `input_variables.properties.${key}.name`,
                message: `Variable name ${variable.name} format is incorrect, can only contain letters, numbers and underscores`,
                type: 'error',
                code: 'VARIABLE_NAME_INVALID'
            });
        }
    });

    return { isValid: errors.length === 0, errors };
};

/**
 * Validate output variables
 */
export const validateOutputVariables = (output_variables: any): ValidationResult => {
    const errors: ValidationError[] = [];

    // Check if output variables exist
    if (!output_variables) {
        errors.push({
            field: 'output_variables',
            message: 'Output variables cannot be empty',
            type: 'error',
            code: 'OUTPUT_VARIABLES_REQUIRED'
        });
        return { isValid: false, errors };
    }

    // Check if properties exist and are not empty
    if (!output_variables.properties || _.isEmpty(output_variables.properties)) {
        errors.push({
            field: 'output_variables.properties',
            message: 'At least one output variable must be defined',
            type: 'error',
            code: 'OUTPUT_VARIABLES_EMPTY'
        });
        return { isValid: false, errors };
    }

    // Check for duplicate variable names
    const variableNames = Object.keys(output_variables.properties);
    const duplicateNames = findDuplicates(variableNames);
    if (duplicateNames.length > 0) {
        errors.push({
            field: 'output_variables.properties',
            message: `Duplicate variable names: ${duplicateNames.join(', ')}`,
            type: 'error',
            code: 'OUTPUT_VARIABLES_DUPLICATE'
        });
    }

    // Validate basic information for each variable
    Object.entries(output_variables.properties).forEach(([key, variable]: [string, any]) => {
        if (!variable.name || variable.name.trim() === '') {
            errors.push({
                field: `output_variables.properties.${key}.name`,
                message: `Variable ${key} name cannot be empty`,
                type: 'error',
                code: 'VARIABLE_NAME_REQUIRED'
            });
        }

        if (!variable.display_name || variable.display_name.trim() === '') {
            errors.push({
                field: `output_variables.properties.${key}.display_name`,
                message: `Variable ${key} display name cannot be empty`,
                type: 'error',
                code: 'VARIABLE_DISPLAY_NAME_REQUIRED'
            });
        }

        // Validate variable name format
        if (variable.name && !/^[a-zA-Z0-9_]+$/.test(variable.name)) {
            errors.push({
                field: `output_variables.properties.${key}.name`,
                message: `Variable name ${variable.name} format is incorrect, can only contain letters, numbers and underscores`,
                type: 'error',
                code: 'VARIABLE_NAME_INVALID'
            });
        }
    });

    return { isValid: errors.length === 0, errors };
};

/**
 * Validate code
 */
export const validateCode = (code: string): ValidationResult => {
    const errors: ValidationError[] = [];

    if (!code || code.trim() === '') {
        errors.push({
            field: 'code',
            message: 'Code cannot be empty',
            type: 'error',
            code: 'CODE_REQUIRED'
        });
        return { isValid: false, errors };
    }

    try {
        const parsedCode = JSON.parse(code);
        if (!parsedCode.python3 || parsedCode.python3.trim() === '') {
            errors.push({
                field: 'code.python3',
                message: 'Python code cannot be empty',
                type: 'error',
                code: 'PYTHON_CODE_REQUIRED'
            });
        }

        // Basic Python syntax check (check if main function is included)
        if (parsedCode.python3 && !parsedCode.python3.includes('def main(')) {
            errors.push({
                field: 'code.python3',
                message: 'Code must contain main function definition',
                type: 'warning',
                code: 'MAIN_FUNCTION_MISSING'
            });
        }
    } catch (e) {
        errors.push({
            field: 'code',
            message: 'Code format is incorrect, cannot parse JSON',
            type: 'error',
            code: 'CODE_INVALID_JSON'
        });
    }

    return { isValid: errors.length === 0, errors };
};

/**
 * Validate basic information (removed description validation)
 */
export const validateBasicInfo = (skillData: SkillData): ValidationResult => {
    const errors: ValidationError[] = [];

    if (!skillData.name || skillData.name.trim() === '') {
        errors.push({
            field: 'name',
            message: 'Skill name cannot be empty',
            type: 'error',
            code: 'NAME_REQUIRED'
        });
    }

    return { isValid: errors.length === 0, errors };
};

/**
 * Full data validation
 */
export const validateSkillData = (skillData: SkillData): ValidationResult => {
    const allErrors: ValidationError[] = [];

    // Validate basic information
    const basicResult = validateBasicInfo(skillData);
    allErrors.push(...basicResult.errors);

    // Validate input variables
    const inputResult = validateInputVariables(skillData.input_variables);
    allErrors.push(...inputResult.errors);

    // Validate output variables
    const outputResult = validateOutputVariables(skillData.output_variables);
    allErrors.push(...outputResult.errors);

    // Validate code
    // if (skillData.code) {
    //     const codeResult = validateCode(skillData.code);
    //     allErrors.push(...codeResult.errors);
    // }

    return {
        isValid: allErrors.length === 0,
        errors: allErrors
    };
};

/**
 * Get internationalization key for error message
 */
export const getErrorMessageKey = (errorCode: string): string => {
    const errorKeyMap: Record<string, string> = {
        'INPUT_VARIABLES_REQUIRED': 'skill.message.inputerror1',
        'INPUT_VARIABLES_EMPTY': 'skill.message.inputerror1',
        'OUTPUT_VARIABLES_REQUIRED': 'skill.message.inputerror2',
        'OUTPUT_VARIABLES_EMPTY': 'skill.message.inputerror2',
        'INPUT_VARIABLES_DUPLICATE': 'skill.message.inputerror5',
        'OUTPUT_VARIABLES_DUPLICATE': 'skill.message.inputerror5',
        'VARIABLE_NAME_REQUIRED': 'skill.rules.name',
        'VARIABLE_DISPLAY_NAME_REQUIRED': 'skill.rules.displayname',
        'VARIABLE_NAME_INVALID': 'skill.rules.verifydescription',
        'CODE_REQUIRED': 'skill.message.codeerror',
        'PYTHON_CODE_REQUIRED': 'skill.message.codeerror',
        'NAME_REQUIRED': 'skill.message.nameerror',
        'MAIN_FUNCTION_MISSING': 'skill.message.mainfunction.missing'
    };
    
    return errorKeyMap[errorCode] || 'skill.message.defaulterror';
}; 