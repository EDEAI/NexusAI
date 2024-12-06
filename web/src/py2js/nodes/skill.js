/*
 * @LastEditors: biz
 */
// Import necessary modules
import { ObjectVariable } from '../variables.js';
import { Node } from './base.js';

/**
 * A SkillNode object is used to integrate external skills into the workflow.
 */
class SkillNode extends Node {
   /**
 * Initialize a SkillNode object.
 * @param {number} skill_id - The ID of the skill.
 * @param {string} title - The title of the node.
 * @param {string} desc - The description of the node.
 * @param {ObjectVariable} input - The type of input variable.
 * @param {ObjectVariable} output - The type of output variable.
 * @param {boolean} wait_for_all_predecessors - Whether to wait for all predecessor nodes.
 * @param {boolean} manual_confirmation - Whether manual confirmation is required.
 * @param {Object.<string, any>} flow_data - The flow data.
 * @param {string} original_node_id - The original node ID.
 */
    constructor({
        skill_id = 0,
        title = '',
        desc = '',
        input = null,
        output = null,
        wait_for_all_predecessors = false,
        manual_confirmation = false,
        flow_data = {},
        original_node_id = null,
    }) {
        /**
         * Initializes a SkillNode object.
         */
        const init_kwargs = {
            type: 'skill',
            skill_id: skill_id,
            title: title,
            desc: desc,
            input: input,
            output: output,
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

export default SkillNode;
