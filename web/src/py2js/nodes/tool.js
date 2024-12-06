/*
 * @LastEditors: biz
 */
// Import necessary modules
import { ObjectVariable } from '../variables.js';
import { Node } from './base.js';

/**
 * A ToolNode object is used to integrate external tools into the workflow.
 */
class ToolNode extends Node {
    /**
     * Initializes a ToolNode object.
  
     *
     * @param {string} title - The title of the node.
     * @param {string} desc - The description of the node.
     * @param {ObjectVariable} input - The input variable.
     * @param {Object.<string, string>} tool - The tool configuration.
     * @param {boolean} wait_for_all_predecessors - Whether to wait for all predecessors.
     * @param {boolean} manual_confirmation - Whether manual confirmation is required.
     * @param {Object.<string, any>} flow_data - The flow data.
     * @param {string} original_node_id - The original node ID.
     */
    constructor({
        title = '',
        desc = '',
        input = null,
        tool = {},
        wait_for_all_predecessors = false,
        manual_confirmation = false,
        flow_data = {},
        original_node_id = null,
    }) {
        /**
         * Initializes a ToolNode object.
         */
        const init_kwargs = {
            type: 'tool',
            title: title,
            desc: desc,
            input: input,
            tool: tool,
            wait_for_all_predecessors: wait_for_all_predecessors,
            manual_confirmation: manual_confirmation,
            flow_data: flow_data,
        };
        if (original_node_id !== null) {
            init_kwargs.original_node_id = original_node_id;
        }

        super(init_kwargs);
    }
}

export default ToolNode;
