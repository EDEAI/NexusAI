/*
 * @LastEditors: biz
 */
// httpRequestNode.js

import { ObjectVariable } from '../variables.js';
import { Node } from './base.js';

/**
 * A HttpRequestNode object is used to make HTTP requests to external APIs.
 */
class HttpRequestNode extends Node {
    /**
     * Initializes an HttpRequestNode object.
     * The backend output defaults to a Variable of type string, with the variable name 'output'.
     *
     * @param {string} title - The title of the HTTP request node.
     * @param {string} [desc=""] - The description of the HTTP request node, default is an empty string.
     * @param {ObjectVariable} [input=null] - The type of input variable, default is null.
     * @param {boolean} [wait_for_all_predecessors=false] - Whether to wait for all predecessor nodes to complete, default is false.
     * @param {boolean} [manual_confirmation=false] - Whether manual confirmation is required, default is false.
     * @param {Object.<string, any>} [flow_data={}] - Flow data, default is an empty object.
     * @param {string} [original_node_id=null] - The original node ID, default is null.
     */
    constructor({
        title,
        desc = '',
        input = null,
        wait_for_all_predecessors = false,
        manual_confirmation = false,
        flow_data = {},
        original_node_id = null,
    }) {
        const init_kwargs = {
            type: 'http_request',
            title: title,
            desc: desc,
            input: input,
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

export default HttpRequestNode;
