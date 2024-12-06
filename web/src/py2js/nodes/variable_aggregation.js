/*
 * @LastEditors: biz
 */
import { VariableTypes } from '../variables.js';
import { Node } from './base.js';

/**
 * A VariableAggregationNode object is used to aggregate variables from multiple sources.
 */
export default class VariableAggregationNode extends Node {
    /**
     * Initialize a VariableAggregationNode object with enhanced typing and the ability to track the original node ID.
     * The backend output defaults to a variable named 'output', and the variable type depends on the entry branch variable at runtime.
     *
     * @param {string} title - The title of the node.
     * @param {string} [desc=""] - The description of the node, defaulting to an empty string.
     * @param {VariableTypes} [input=null] - The type of input variable.
     * @param {Object.<string, any>} flow_data - The flow data.
     * @param {string|null} [original_node_id=null] - The original node ID, if any.
     */
    constructor({ title, desc = '', input = null, flow_data = {}, original_node_id = null }) {
        // Constructing the initialization object
        const initKwargs = {
            type: 'variable_aggregation',
            title,
            desc,
            input,
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
