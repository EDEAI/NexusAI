/*
 * @LastEditors: biz
 */
import { Variable } from './variables.js';

export class Prompt {
   /**
 * Represents a prompt containing system, user, and assistant properties.
 * The values of each property can include placeholders, which will be replaced by the actual values from the Context object.
 * @param {string} [system=""] - The system part of the prompt.
 * @param {string} [user=""] - The user part of the prompt.
 * @param {string} [assistant=""] - The assistant part of the prompt.
 */
    constructor(system = '', user = '', assistant = '') {
        this.system = system ? new Variable('system', 'string', system) : null;
        this.user = user ? new Variable('user', 'string', user) : null;
        this.assistant = assistant ? new Variable('assistant', 'string', assistant) : null;
        // console.log(this.system, this.user, this.assistant);
    }

    /**
     * Returns the system's part of the prompt.
     * @returns {string} The system's part of the prompt.
     */
    getSystem() {
        return this.system ? this.system.value : '';
    }

    /**
     * Returns the user's part of the prompt.
     * @returns {string} The user's part of the prompt.
     */
    getUser() {
        return this.user ? this.user.value : '';
    }

    /**
     * Returns the assistant's part of the prompt.
     * @returns {string} The assistant's part of the prompt.
     */
    getAssistant() {
        return this.assistant ? this.assistant.value : '';
    }

    /**
     * Converts the Prompt object to a plain object.
     * @returns {Object} A plain object representation of the Prompt object.
     */
    toObject() {
        return {
            system: this.system ? this.system.toObject() : null,
            user: this.user ? this.user.toObject() : null,
            assistant: this.assistant ? this.assistant.toObject() : null,
        };
    }
}

/**
 * Creates a Prompt object from a plain object representation.
 * @param {Object} promptObj - A plain object representing a Prompt.
 * @returns {Prompt} An instance of the Prompt class.
 */
export function createPromptFromObject(promptObj) {
    console.log(promptObj);
    return new Prompt(
        promptObj.system ? promptObj.system.value : '',
        promptObj.user ? promptObj.user.value : '',
        promptObj.assistant ? promptObj.assistant.value : '',
    );
}
