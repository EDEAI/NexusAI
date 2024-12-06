/*
 * @LastEditors: biz
 */
// Importing necessary modules and classes
import { VariableTypes } from '../variables.js';
import { Node } from './base.js';

/**
 * Class representing an EndNode, used to mark the end of the workflow.
 */
class EndNode extends Node {
    /**
 * Initializes a new instance of the EndNode class.
 * @param {Object} options - Options for initializing the EndNode.
 * @param {string} options.title - The title of the node.
 * @param {string} [options.desc=""] - The description of the node.
 * @param {VariableTypes} [options.output=null] - The type of output variable for the node.
 * @param {boolean} [options.wait_for_all_predecessors=true] - Indicates whether the node should wait for all predecessor nodes.
 * @param {boolean} [options.manual_confirmation=false] - Indicates whether manual confirmation is required.
 * @param {Object} [options.position={}] - The position of the node on the canvas.
 * @param {number} [options.width=0] - The width of the node.
 * @param {number} [options.height=0] - The height of the node.
 * @param {boolean} [options.selected=false] - Indicates whether the node is selected.
 * @param {string|null} [options.original_node_id=null] - The original node ID if this is a copy.
 */
    constructor({
        title,
        desc = '',
        output = null,
        wait_for_all_predecessors = true,
        manual_confirmation = false,
        width = 0,
        height = 0,
        selected = false,
        original_node_id = null,
    }) {
        // Constructing the initialization object
        const init_kwargs = {
            type: 'end',
            title,
            desc,
            output,
            wait_for_all_predecessors,
            manual_confirmation,
        };

        // Adding the original node ID if provided
        if (original_node_id !== null) {
            init_kwargs.original_node_id = original_node_id;
        }

        // Calling the parent class constructor
        super(init_kwargs);
    }
}

// Exporting the EndNode class for use in other modules
export default EndNode;
