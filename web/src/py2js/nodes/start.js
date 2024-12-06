/*
 * @LastEditors: biz
 */
// Importing necessary modules
import { ObjectVariable } from '../variables.js';
import { Node } from './base.js';

/**
 * Class representing the start of a workflow.
 */
class StartNode extends Node {
    /**
 * Initialize a new StartNode instance.
 * The input and output remain consistent.
 *
 * @param {string} title - The title of the node.
 * @param {string} [desc=""] - The description of the node, defaulting to an empty string.
 * @param {ObjectVariable} [input=null] - The input variable of the node, defaulting to null.
 * @param {ObjectVariable} [output=null] - The output variable of the node, which is emphasized as output, not an input, defaulting to null.
 * @param {boolean} [requires_upload=false] - Flag indicating whether the node requires uploading, defaulting to false.
 * @param {Object.<string, boolean>} [import_to_knowledge_base={}] - Mapping of whether to import to the knowledge base, defaulting to an empty object.
 * @param {Object.<string, Object.<string, number|Object.<string, number>>} [knowledge_base_mapping={}] - The knowledge base mapping, defaulting to an empty object.
 * @param {Object.<string, any>} [flow_data={}] - The flow data, defaulting to an empty object.
 * @param {string|null} [originalNodeId=null] - The original node ID if this is a copy, defaulting to null.
 */
    constructor({
        title,
        desc = '',
        input = null,
        output = null,
        requires_upload = false,
        import_to_knowledge_base = {},
        knowledge_base_mapping = {},
        flow_data = {},
        original_node_id = null,
    }) {
        // Constructing the initialization object
        const init_kwargs = {
            type: 'start',
            title,
            desc,
            input,
            output,
            requires_upload,
            import_to_knowledge_base,
            knowledge_base_mapping,
            flow_data,
        };

        // Adding the original node ID if provided
        if (original_node_id !== null) {
            init_kwargs.original_node_id = original_node_id;
        }

        // Calling the parent class constructor
        super(init_kwargs);
    }
}

// Exporting the StartNode class for use in other modules
export default StartNode;
