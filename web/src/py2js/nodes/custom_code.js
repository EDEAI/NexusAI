/*
 * @LastEditors: biz
 */
// Import necessary modules
import { ObjectVariable } from '../variables.js';
import { Node } from './base.js';

/**
 * A class representing custom JavaScript code execution in a workflow.
 */
class CustomCodeNode extends Node {
    /**
     * Initializes a CustomCodeNode object.
     * @param {string} title - The title of the node.
     * @param {string} desc - The description of the node.
     * @param {ObjectVariable} input - The type of input variable.
     * @param {Object.<string, Array.<string>>} code_dependencies - Code dependencies.
     * @param {Object.<string, string>} custom_code - Custom code.
     * @param {ObjectVariable} output - The type of output variable.
     * @param {boolean} wait_for_all_predecessors - Whether to wait for all predecessor nodes.
     * @param {boolean} manual_confirmation - Whether manual confirmation is required.
     * @param {Object.<string, any>} flow_data - Flow data.
     * @param {string} original_node_id - The original node ID.
     */
    constructor({
        title = '',
        desc = '',
        input = null,
        code_dependencies = {},
        custom_code = {},
        output = null,
        wait_for_all_predecessors = false,
        manual_confirmation = false,
        flow_data = {},
        original_node_id = null,
    }) {
        const init_kwargs = {
            type: 'custom_code',
            title: title,
            desc: desc,
            input: input,
            code_dependencies: code_dependencies,
            custom_code: custom_code,
            output: output,
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

export default CustomCodeNode;
