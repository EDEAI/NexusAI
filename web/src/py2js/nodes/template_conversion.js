/*
 * @LastEditors: biz
 */
// Import necessary modules
import { ObjectVariable } from '../variables.js';
import { Node } from './base.js';

/**
 * This node is responsible for converting data into a fixed string format using Jinja2 template code.
 */
class TemplateConversionNode extends Node {
    /**
     * Initialize a TemplateConversionNode object.
     * The backend output defaults to a string type Variable named 'output'.
     *
     * @param {string} title - The title of the node.
     * @param {string} desc - The description of the node.
     * @param {ObjectVariable} input - The input variables.
     * @param {Object.<string, string>} custom_code - Custom code.
     * @param {boolean} wait_for_all_predecessors - Whether to wait for all predecessor nodes to complete.
     * @param {boolean} manual_confirmation - Whether manual confirmation is required.
     * @param {Object.<string, any>} flow_data - The flow data.
     * @param {string} original_node_id - The original node ID.
     */
    constructor({
        title = '',
        desc = '',
        input = null,
        custom_code = {},
        wait_for_all_predecessors = false,
        manual_confirmation = false,
        flow_data = {},
        original_node_id = null,
    }) {
        /**
         * Initializes a TemplateConversionNode object.
         */
        const init_kwargs = {
            type: 'template_conversion',
            title: title,
            desc: desc,
            input: input,
            custom_code: custom_code,
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

export default TemplateConversionNode;
