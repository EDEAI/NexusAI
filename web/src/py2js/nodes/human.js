/*
 * @LastEditors: biz
 */
// Importing necessary modules and classes
import { ObjectVariable } from '../variables.js';
import { Node } from './base.js';

/**
 * A HumanNode object is used to create manual confirmation tasks in a workflow.
 */
class HumanNode extends Node {
    /**
     * Initializes a human node object with specific parameters for manual confirmation tasks.
     * The input and output remain consistent.
     *
     * @param {string} title - The title of the human node.
     * @param {string} [desc=""] - The description of the human node.
     * @param {ObjectVariable} [input=null] - The input variable.
     * @param {ObjectVariable} [output=null] - The output variable.
     * @param {boolean} [requires_upload=false] - Whether the node requires an upload.
     * @param {boolean} [wait_for_all_predecessors=false] - Whether to wait for all predecessor nodes.
     * @param {boolean} [manual_confirmation=true] - Whether manual confirmation is required.
     * @param {boolean} [import_to_knowledge_base=false] - Whether to import into the knowledge base.
     * @param {Object.<string, number>} [knowledge_base_mapping={}] - The knowledge base mapping.
     * @param {Object.<string, any>} [flow_data={}] - The flow data.
     * @param {string} [original_node_id=null] - The original node ID.
     */
    constructor({
        title,
        desc = '',
        input = null,
        output = null,
        requires_upload = false,
        wait_for_all_predecessors = false,
        manual_confirmation = true,
        import_to_knowledge_base = {},
        knowledge_base_mapping = {},
        flow_data = {},
        original_node_id = null,
    }) {
        const init_args = {
            type: 'human',
            title: title,
            desc: desc,
            input: input,
            output: output,
            requires_upload: requires_upload,
            wait_for_all_predecessors: wait_for_all_predecessors,
            manual_confirmation: manual_confirmation,
            import_to_knowledge_base: import_to_knowledge_base,
            knowledge_base_mapping: knowledge_base_mapping,
            flow_data: flow_data,
        };
        if (original_node_id !== null) {
            init_args.original_node_id = original_node_id;
        }

        super(init_args);
    }
}
export default HumanNode;
