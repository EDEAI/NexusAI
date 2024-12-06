/*
 * @LastEditors: biz
 */
// retrieverNode.js

import { VariableTypes } from '../variables.js';
import { Node } from './base.js';

/**
 * A RetrieverNode object is used to retrieve data from a knowledge base.
 */
class RetrieverNode extends Node {
    /**
 * Initialize a RetrieverNode object.
 * The backend output defaults to an array of object type ArrayVariable named 'output'.
 *
 * @param {string} title - The title of the retriever node.
 * @param {string} [desc=""] - The description of the retriever node.
 * @param {VariableTypes} [input=null] - The input variables.
 * @param {number[]} [datasets=[]] - The datasets to be retrieved.
 * @param {boolean} [manual_confirmation=false] - Whether manual confirmation is required.
 * @param {Object.<string, any>} [flow_data={}] - The flow data.
 * @param {string} [original_node_id=null] - The original node ID.
 */
    constructor({
        title,
        desc = '',
        input = null,
        datasets = [],
        manual_confirmation = false,
        flow_data = {},
        original_node_id = null,
    }) {
        const init_kwargs = {
            type: 'retriever',
            title: title,
            desc: desc,
            input: input,
            datasets: datasets,
            manual_confirmation: manual_confirmation,
            flow_data: flow_data,
        };
        if (original_node_id !== null) {
            init_kwargs.original_node_id = original_node_id;
        }

        super(init_kwargs);
    }
}

export default RetrieverNode;
