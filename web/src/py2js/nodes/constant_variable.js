/*
 * @LastEditors: biz
 */
import { ObjectVariable } from '../variables.js';
import { Node } from './base.js';

/**
 * A ConstantVariableNode object is used to define constant variables that can be reused in a workflow.
 * This helps avoid the need to repeatedly input the same variables when running a workflow multiple times.
 */
export default class ConstantVariableNode extends Node {
    /**
     * Initialize a ConstantVariableNode object.
     * 
     * @param {string} title - The title of the node.
     * @param {string} [desc=""] - The description of the node, defaulting to an empty string.
     * @param {ObjectVariable} [input=null] - The input variables that will be used as constants.
     * @param {ObjectVariable} [output=null] - The output variables (same as input for constants).
     * @param {Object.<string, any>} flow_data - The flow data.
     * @param {string|null} [original_node_id=null] - The original node ID, if any.
     */
    constructor({ title, desc = '', input = null, output = null, flow_data = {}, original_node_id = null }) {
        // Constructing the initialization object
        const initKwargs = {
            type: 'constant_variable',
            title,
            desc,
            input,
            output,
            flow_data,
        };

        // Adding the original node ID if provided
        if (original_node_id !== null) {
            initKwargs.original_node_id = original_node_id;
        }

        // Calling the parent class constructor
        super(initKwargs);
    }
} 