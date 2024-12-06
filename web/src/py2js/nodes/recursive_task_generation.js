/*
 * @LastEditors: biz
 */
// Import necessary modules
import { Prompt } from '../prompt.js';
import { VariableTypes } from '../variables.js';
import { Node } from './base.js';

/**
 * A RecursiveTaskGenerationNode object is used to generate recursive tasks in a workflow.
 */
class RecursiveTaskGenerationNode extends Node {
    /**
 * Initialize a RecursiveTaskGenerationNode object with enhanced typing capabilities and the ability to track the original node ID.
 * @param {string} title - The title of the node.
 * @param {string} desc - The description of the node.
 * @param {VariableTypes} input - The input variables.
 * @param {number} model_config_id - The model configuration ID.
 * @param {number} category_purpose - The category purpose.
 * @param {Prompt} prompt - The prompt object.
 * @param {boolean} requires_upload - Whether the node requires uploading.
 * @param {boolean} manual_confirmation - Whether manual confirmation is required.
 * @param {Object.<string, boolean>} import_to_knowledge_base - Whether to import to the knowledge base.
 * @param {Object.<string, Object.<string, number|Object.<string, number>>>} knowledge_base_mapping - The knowledge base mapping.
 * @param {Object.<string, any>} flow_data - The flow data.
 * @param {string} original_node_id - The original node ID.
 */
    constructor({
        title,
        desc = '',
        input = null,
        model_config_id = 0,
        // category_purpose = 1,
        prompt = null,
        requires_upload = false,
        manual_confirmation = false,
        import_to_knowledge_base = {},
        knowledge_base_mapping = {},
        flow_data = {},
        original_node_id = null,
    }) {
        const init_kwargs = {
            type: 'recursive_task_generation',
            title: title,
            desc: desc,
            input: input,
            model_config_id: model_config_id,
            // category_purpose: category_purpose,
            prompt: prompt,
            requires_upload: requires_upload,
            manual_confirmation: manual_confirmation,
            import_to_knowledge_base: import_to_knowledge_base,
            knowledge_base_mapping: knowledge_base_mapping,
            flow_data: flow_data,
        };
        if (original_node_id !== null) {
            init_kwargs.original_node_id = original_node_id;
        }

        super(init_kwargs);
    }
}

export default RecursiveTaskGenerationNode;
