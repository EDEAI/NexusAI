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
        return data;
    }
}

/**
 * Represents an array variable with a name, display name, type, and a list of values.
 * @class
 */
export class ArrayVariable {
    // Constructor to create an instance of ArrayVariable
    constructor(name, type, display_name = undefined) {
        this.name = name; // Name of the array variable
        this.type = type; // Type of the array elements
        this.values = []; // List of array values
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
    constructor(name, display_name = undefined, to_string_keys = undefined) {
        this.name = name; // Name of the object variable
        this.type = 'object'; // Object type
        this.properties = {}; // Dictionary of properties
        if (display_name !== undefined) {
            this.display_name = display_name; // Display name of the object variable
        }
        if (to_string_keys !== undefined) {
            this.to_string_keys = to_string_keys; // Keys to be converted to string
        }
    }

    // Method to add a new property to the object
    addProperty(key, value) {
        this.properties[key] = value; // Add property to the object
    }

    // Method to convert the ObjectVariable object to a JavaScript object
    toObject() {
        const data = {
            name: this.name,
            type: this.type,
            properties: {}, // Initialize the properties dictionary
        };
        // Iterate over properties and convert them to object form
        for (const key in this.properties) {
            data.properties[key] = this.properties[key].toObject();
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
        if ('to_string_keys' in data) variableArgs.push(data.to_string_keys);
        let objVar = new ObjectVariable(...variableArgs);
        for (let [key, value] of Object.entries(data.properties)) {
            objVar.addProperty(key, createVariableFromObject(value));
        }
        console.log(objVar);
        return objVar;
    } else if (data.type.startsWith('array')) {
        let variableArgs = [data.name, data.type];
        if ('display_name' in data) variableArgs.push(data.display_name);
        let arrVar = new ArrayVariable(...variableArgs);
        for (let value of data.values) {
            arrVar.addValue(createVariableFromObject(value));
        }
        return arrVar;
    } else {
        let variableArgs = [data.name, data.type, data.value];
        if ('display_name' in data) variableArgs.push(data.display_name);
        if ('required' in data) variableArgs.push(data.required);
        if (data.type === 'string' && 'max_length' in data) variableArgs.push(data.max_length);
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
