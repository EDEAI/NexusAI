/**
 * 。
 * @class
 */
export class Variable {
    // Constructor to create an instance of Variable
    constructor(
        name,
        type,
        value = null,
        display_name = undefined,
        required = undefined,
        max_length = 0,
        sort_order = 0,
        description = undefined
    ) {
        this.name = name; // Variable name
        this.type = type; // Variable type, can be 'string', 'number', or 'file/json'
        this.value = value; // Variable value
        if (display_name !== undefined) {
            this.display_name = display_name; // Display name of the variable
        }
        if (required !== undefined) {
            this.required = required; // Indicates if the variable is required
        }
        this.sort_order = sort_order; // Sort order of the variable
        if (description !== undefined) {
            this.description = description;
        }
        if (this.type === 'string') {
            this.max_length = max_length; // Maximum length for string variables
            if (this.max_length > 0 && this.value.length > this.max_length) {
                throw new Error(`String length exceeds maximum length of ${this.max_length}`); // Throws an error if the string length exceeds the maximum
            }
        }
    }

    // Method to convert the Variable object to a JavaScript object
    toObject() {
        const data = {
            name: this.name,
            type: this.type,
            value: this.value,
            sort_order: this.sort_order,
        };
        if ('display_name' in this) {
            data.display_name = this.display_name;
        }
        if ('required' in this) {
            data.required = this.required;
        }
        if (this.type == 'string' && 'max_length' in this) {
            data.max_length = this.max_length;
        }
        if ('description' in this) {
            data.description = this.description;
        }
        return data;
    }
}

/**
 * Represents an array variable with a name, display name, type, and a list of values.
 * @class
 */
export class ArrayVariable {
    // Constructor to create an instance of ArrayVariable
    constructor(name, type, display_name = undefined, sort_order = 0) {
        this.name = name; // Name of the array variable
        this.type = type; // Type of the array elements
        this.values = []; // List of array values
        this.sort_order = sort_order; // Order for displaying the variable
        if (display_name !== undefined) {
            this.display_name = display_name; // Display name of the array variable
        }
    }

    // Method to add a new value to the array if it matches the element type
    addValue(value) {
        let elementType = this.type.split('[')[1].split(']')[0]; // Retrieve the array element type
        if (value.type === elementType) {
            this.values.push(value); // Add value to the array
        } else {
            throw new Error(`Value must be of type ${elementType} as specified in type`); // Throw error if type does not match
        }
    }

    // Method to convert the ArrayVariable object to a JavaScript object representation
    toObject() {
        const data = {
            name: this.name,
            type: this.type,
            values: this.values.map(value => value.toObject()), // Convert list of values to object list
            sort_order: this.sort_order,
        };
        if ('display_name' in this) {
            data.display_name = this.display_name;
        }
        return data;
    }
}

/**
 * Represents an object variable with a name, display name, type, and a dictionary of properties.
 * @class
 */
export class ObjectVariable {
    // Constructor to create an instance of ObjectVariable
    constructor(name, display_name = undefined, to_string_keys = undefined, sort_order = 0) {
        this.name = name; // Name of the object variable
        this.type = 'object'; // Object type
        this.properties = {}; // Dictionary of properties
        this.sort_order = sort_order; // Order for displaying the variable
        if (display_name !== undefined) {
            this.display_name = display_name; // Display name of the object variable
        }
        if (to_string_keys !== undefined) {
            this.to_string_keys = to_string_keys; // Keys to be converted to string
        }
    }

    // Method to add a new property to the object
    addProperty(key, value) {
        // If sort_order not set or zero, assign next available order number
        if (value.sort_order === undefined || value.sort_order === 0) {
            // Find the maximum sort_order currently in use
            let currentMax = 0;
            for (const prop in this.properties) {
                currentMax = Math.max(currentMax, this.properties[prop].sort_order || 0);
            }
            // Assign next sort_order value
            value.sort_order = currentMax + 1;
        }
        
        this.properties[key] = value; // Add property to the object
    }

    // Method to convert the ObjectVariable object to a JavaScript object
    toObject() {
        // Sort properties by sort_order
        const sortedEntries = Object.entries(this.properties).sort((a, b) => {
            const aOrder = a[1].sort_order || 0;
            const bOrder = b[1].sort_order || 0;
            return aOrder - bOrder;
        });
        
        const data = {
            name: this.name,
            type: this.type,
            properties: {}, // Initialize the properties dictionary
            sort_order: this.sort_order,
        };
        
        // Iterate over sorted properties and convert them to object form
        for (const [key, value] of sortedEntries) {
            data.properties[key] = value.toObject();
        }
        
        if ('display_name' in this) {
            data.display_name = this.display_name;
        }
        if ('to_string_keys' in this) {
            data.to_string_keys = this.to_string_keys;
        }
        return data;
    }
}

/**
 * Method to create a VariableTypes object from a dictionary.
 * @param {Object} data - The dictionary used to create the VariableTypes object.
 * @returns {VariableTypes} The created VariableTypes object.
 */
export function createVariableFromObject(data) {
    // Create different types of variables based on the data type
    if (data.type === 'object') {
        let variableArgs = [data.name];
        if ('display_name' in data) variableArgs.push(data.display_name);
        else variableArgs.push(undefined);
        
        if ('to_string_keys' in data) variableArgs.push(data.to_string_keys);
        else variableArgs.push(undefined);
        
        if ('sort_order' in data) variableArgs.push(data.sort_order);
        
        let objVar = new ObjectVariable(...variableArgs);
        for (let [key, value] of Object.entries(data.properties)) {
            objVar.addProperty(key, createVariableFromObject(value));
        }
        return objVar;
    } else if (data.type.startsWith('array')) {
        let variableArgs = [data.name, data.type];
        if ('display_name' in data) variableArgs.push(data.display_name);
        else variableArgs.push(undefined);
        
        if ('sort_order' in data) variableArgs.push(data.sort_order);
        
        let arrVar = new ArrayVariable(...variableArgs);
        for (let value of data.values) {
            arrVar.addValue(createVariableFromObject(value));
        }
        return arrVar;
    } else {
        let variableArgs = [data.name, data.type, data.value];
        if ('display_name' in data) variableArgs.push(data.display_name);
        else variableArgs.push(undefined);
        
        if ('required' in data) variableArgs.push(data.required);
        else variableArgs.push(undefined);
        
        if (data.type === 'string' && 'max_length' in data) variableArgs.push(data.max_length);
        else variableArgs.push(0);
        
        const sortOrder = 'sort_order' in data ? data.sort_order : 0;
        variableArgs.push(sortOrder);
        if ('description' in data) variableArgs.push(data.description);
        
        return new Variable(...variableArgs);
    }
}

/**
 * Validates that all required variables have values. If a required variable has no value, raises an Error.
 *
 * @param {Variable|ArrayVariable|ObjectVariable} variable - An instance of Variable, ArrayVariable, or ObjectVariable.
 * @throws {Error} If a required variable has no value.
 */
function validateRequiredVariable(variable) {
    if (variable instanceof Variable) {
        if (variable.required && (variable.value === null || variable.value === '')) {
            throw new Error(`Variable ${variable.name} is required but has no value.`);
        }
    } else if (variable instanceof ArrayVariable) {
        for (const value of variable.values) {
            validateRequiredVariable(value);
        }
    } else if (variable instanceof ObjectVariable) {
        for (const key in variable.properties) {
            validateRequiredVariable(variable.properties[key]);
        }
    }
}

/**
 * @typedef {Variable|ArrayVariable|ObjectVariable} VariableTypes - Represents a type that can be Variable, ArrayVariable, or ObjectVariable.
 */

export default {
    Variable,
    ArrayVariable,
    ObjectVariable,
    createVariableFromObject,
    validateRequiredVariable,
};
