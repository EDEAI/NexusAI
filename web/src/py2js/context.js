/*
 * @LastEditors: biz
 */

// Import necessary modules and classes
import { Node } from './nodes/base.js';
import { createVariableFromObject } from './variables.js';

/**
 * Represents the inputs and outputs of all nodes in a workflow.
 */
export class Context {
    /**
     * Initialize a new instance of the Context class.
     */
    constructor() {
        // Initialize an empty array to store input and output records of nodes
        this.records = [];
    }

    /**
     * Add the input and output data of a node to the records.
     *
     * @param {Number} level - The level of the node in the workflow
     * @param {Node} node - The node object.
     */
    addNode(level, node) {
        // Add an object containing the node's level, ID, title, type, and inputs/outputs to the records array
        this.records.push({
            level: level,
            node_id: node.id,
            node_title: node.data['title'],
            node_type: node.data['type'],
            inputs: node.data.input ? node.data.input : null, // Store if the node has input data, otherwise null
            outputs: node.data.output ? node.data.output : null, // Store if the node has output data, otherwise null
        });
    }

    /**
     * Convert the Context object into an object representation.
     * This method ensures that each input and output in the record list is correctly converted into an object representation before being included in the output object.
     *
     * @returns {Object} An object representing the Context object.
     */
    toObject() {
        // Use the map method to convert the records array into a new array of objects and return it
        return this.records.map(record => ({
            level: record.level,
            node_id: record.node_id,
            node_title: record.node_title,
            node_type: record.node_type,
            inputs: record.inputs ? record.inputs.toObject() : null, // Convert to object representation if the node has input data, otherwise null
            outputs: record.outputs ? record.outputs.toObject() : null, // Convert to object representation if the node has output data, otherwise null
        }));
    }

    /**
     * Retrieve records where the level is less than or equal to the given level and node ID is in the given list.
     *
     * @param {Number} level - The current node level.
     * @param {Array<String>} node_ids - A list of node IDs to filter records.
     * @returns {Context} A new Context object containing the filtered records.
     */
    getRelatedRecords(level, node_ids) {
        const newContext = new Context(); // Create a new Context instance
        this.records.forEach(record => {
            // Add the record to the new Context instance's records array if the node's level is less than or equal to the given level and ID is in the list
            if (record.level <= level && node_ids.includes(record.node_id)) {
                newContext.records.push(record);
            }
        });
        return newContext; // Return the new Context instance with filtered records
    }
}

/**
 * Create a Context object from an object representation.
 *
 * @param {Object} contextObj - An object representing the Context object.
 * @returns {Context} An instance of the Context class.
 */
export function createContextFromObject(contextObj) {
    const context = new Context(); // Create a new Context instance
    contextObj.forEach(record => {
        // Iterate over the passed object array, adding each record to the newly created Context instance's records array
        context.records.push({
            level: record.level,
            node_id: record.node_id,
            node_title: record.node_title,
            node_type: record.node_type,
            inputs: record.inputs ? createVariableFromObject(record.inputs) : null, // Use createVariableFromObject method to convert and store if the node has input data, otherwise null
            outputs: record.outputs ? createVariableFromObject(record.outputs) : null, // Use createVariableFromObject method to convert and store if the node has output data, otherwise null
        });
    });
    return context; // Return the newly created Context instance
}