/*
 * @LastEditors: biz
 */
// Importing necessary modules and classes
import { Node } from './base.js';

/**
 * Class representing a node for generating text using a language model.
 */
class LLMNode extends Node {
    /**
 * Initialize a new LLMNode instance.
 * The backend output defaults to a string type Variable with the variable name 'text'.
 *
 * @param {Object} options - Options for initializing the LLMNode.
 * @param {string} options.title - The title of the node.
 * @param {string} [options.desc=""] - The description of the node.
 * @param {ObjectVariable} [input=null] - The input variables.
 * @param {number} [options.model_config_id=0] - The model configuration ID.
 * @param {Prompt|null} [options.prompt=null] - The prompt object for the language model.
 * @param {number[]} [retrieval_task_datasets=[]] - Datasets for task data retrieval.
 * @param {boolean} [options.requires_upload=false] - Indicates whether the node requires file upload.
 * @param {boolean} [options.wait_for_all_predecessors=false] - Indicates whether the node should wait for all predecessor nodes.
 * @param {boolean} [options.task_splitting=false] - Indicates whether task splitting is enabled.
 * @param {boolean} [options.manual_confirmation=false] - Indicates whether manual confirmation is required.
 * @param {Object.<string, boolean>} [import_to_knowledge_base={}] - Whether to import to the knowledge base.
 * @param {Object.<string, Object.<string, number|Object.<string, number>>>} [knowledge_base_mapping={}] - The knowledge base mapping.
 * @param {Object.<string, any>} [flow_data={}] - The flow data.
 * @param {string|null} [options.originalNodeId=null] - The original node ID if this is a copy.
 */
    constructor({
        title,
        desc = '',
        input = null,
        model_config_id = 0,
        prompt = null,
        retrieval_task_datasets = [],
        requires_upload = false,
        wait_for_all_predecessors = false,
        task_splitting = false,
        manual_confirmation = false,
        import_to_knowledge_base = {},
        knowledge_base_mapping = {},
        flow_data = {},
        original_node_id = null,
    }) {
        // Constructing the initialization object
        const init_kwargs = {
            type: 'llm',
            title,
            desc,
            input,
            model_config_id,
            prompt,
            retrieval_task_datasets,
            requires_upload,
            wait_for_all_predecessors,
            task_splitting,
            manual_confirmation,
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

// Exporting the LLMNode class for use in other modules
export default LLMNode;
