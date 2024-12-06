/*
 * @LastEditors: biz
 */
import { VariableTypes } from '../variables.js';
import { Node } from './base.js';

/**
 * A RecursiveTaskExecutionNode object is used to execute recursive tasks in a workflow.
 */
class RecursiveTaskExecutionNode extends Node {
    /**
     * Initialize a RecursiveTaskExecutionNode object.
     * @param {string} title - The title of the node.
     * @param {string} desc - The description of the node.
     * @param {VariableTypes} input - The input variables.
     * @param {number} model_config_id - The model configuration ID.
     * @param {Nodes} executor_list - The list of executors.
     * @param {Prompt} prompt - The prompt object.
     * @param {boolean} manual_confirmation - Whether manual confirmation is required.
     * @param {Object.<string, boolean>} import_to_knowledge_base - Whether to import to the knowledge base.
     * @param {Object.<string, Object.<string, number>>} knowledge_base_mapping - The knowledge base mapping.
     * @param {Object.<string, any>} flow_data - The flow data.
     * @param {string} original_node_id - The original node ID.
     */
    constructor({
        title,
        desc = '',
        input = null,
        model_config_id = 0,
        executor_list = null,
        prompt = null,
        manual_confirmation = false,
        import_to_knowledge_base = {},
        knowledge_base_mapping = {},
        flow_data = {},
        original_node_id = null,
    }) {
        const init_kwargs = {
            type: 'recursive_task_execution',
            title: title,
            desc: desc,
            input: input,
            model_config_id: model_config_id,
            executor_list: executor_list,
            prompt: prompt,
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

export default RecursiveTaskExecutionNode;
