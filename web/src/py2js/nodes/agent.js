/*
 * @LastEditors: biz
 */
// agentNode.js

import { Prompt } from '../prompt.js';
import { ObjectVariable } from '../variables.js';
import { Node } from './base.js';

/**
 * An AgentNode object is used to integrate external agents into the workflow.
 */

class AgentNode extends Node {
    /**
     * Initializes an AgentNode object with the ability to track the original node ID.
     * The backend output defaults to a Variable of type string, with the variable name 'text'.
     *
     * @param {string} title - The title of the agent node.
     * @param {string} [desc=""] - The description of the agent node.
     * @param {ObjectVariable} [input=null] - The type of input variable.
     * @param {number} [agent_id=0] - The agent ID.
     * @param {number} [ability_id=0] - The ability ID.
     * @param {Prompt} [prompt=null] - The prompt object.
     * @param {number[]} [retrieval_task_datasets=[]] - The datasets to be retrieved for task data.
     * @param {boolean} [requires_upload=false] - Whether an upload is required.
     * @param {boolean} [wait_for_all_predecessors=false] - Whether to wait for all predecessors to complete.
     * @param {boolean} [task_splitting=false] - Whether task splitting is enabled.
     * @param {boolean} [manual_confirmation=false] - Whether manual confirmation is required.
     * @param {Object.<string, boolean>} [import_to_knowledge_base={}] - Whether to import into the knowledge base.
     * @param {Object.<string, Object.<string, number|Object.<string, number>>>} [knowledge_base_mapping={}] - The knowledge base mapping.
     * @param {Object.<string, any>} [flow_data={}] - The flow data.
     * @param {string} [original_node_id=null] - The original node ID.
     */
    constructor({
        title,
        desc = '',
        input = null,
        agent_id = 0,
        ability_id = 0,
        prompt = null,
        retrieval_task_datasets = [],
        // requires_upload = false,
        wait_for_all_predecessors = false,
        task_splitting = false,
        manual_confirmation = false,
        import_to_knowledge_base = {},
        knowledge_base_mapping = {},
        flow_data = {},
        original_node_id = null,
    }) {
        const init_kwargs = {
            type: 'agent',
            title: title,
            desc: desc,
            input: input,
            agent_id: agent_id,
            ability_id: ability_id,
            prompt: prompt,
            retrieval_task_datasets: retrieval_task_datasets,
            // requires_upload: requires_upload,
            wait_for_all_predecessors: wait_for_all_predecessors,
            task_splitting: task_splitting,
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

export default AgentNode;
