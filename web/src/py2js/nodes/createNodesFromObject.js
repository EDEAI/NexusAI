import AgentNode from './agent.js';
import { Nodes } from './base.js';
import { createLogicBranchesFromObject, ConditionBranchNode } from './condition_branch.js';
import ConstantVariableNode from './constant_variable.js';
import CustomCodeNode from './custom_code.js';
import EndNode from './end.js';
import HttpRequestNode from './http_request.js';
import HumanNode from './human.js';
import LLMNode from './llm.js';
// import { MemoryInterruptNode } from './memory_interrupt.js';
import {
    createRequirementCategoryFromObject,
    RequirementCategoryNode,
} from './requirement_category.js';
import RetrieverNode from './retriever.js';
import SkillNode from './skill.js';
import StartNode from './start.js';
import TemplateConversionNode from './template_conversion.js';
import ToolNode from './tool.js';
import VariableAggregationNode from './variable_aggregation.js';

import { createPromptFromObject } from '../prompt.js';
import { createVariableFromObject } from '../variables.js';

/**
 * Creates a node instance from the provided object. This function dynamically determines the type of node to create based on the 'type' property of the input object,
 * and then constructs the node using the other properties of the object, adjusting property names and structure as necessary to match the expected constructor parameters of the node class.
 *
 * @param {Object} nodeDict - An object containing node data. This object should include an 'id', a 'data' object containing properties specific to the node type,
 * and a 'type' property within 'data' indicating the type of node to create.
 * @returns {Node} An instance of a Node subclass corresponding to the 'type' specified in nodeDict.data.
 */
function createNodeFromObject(nodeDict) {
    const nodeId = nodeDict.id;
    const nodeData = nodeDict.data;
    const nodeType = nodeData.type;

    delete nodeDict.id;
    delete nodeDict.data;
    delete nodeData.type;

    // Extract and transform specific fields if present, to match Python's detailed logic
    if (nodeData.input) {
        nodeArgs.input = createVariableFromObject(nodeData.input);
    }
    if (nodeData.prompt) {
        nodeArgs.prompt = createPromptFromObject(nodeData.prompt);
    }
    if (nodeData.requirement_category) {
        nodeArgs.requirement_category = createRequirementCategoryFromObject(
            nodeData.requirement_category,
        );
    }
    if (nodeData.logic_branches) {
        nodeArgs.logic_branches = createLogicBranchesFromObject(nodeData.logic_branches);
    }
    if (nodeData.output) {
        nodeArgs.output = createVariableFromObject(nodeData.output);
    }

    // Prepare arguments for node constructor
    const nodeArgs = {
        ...nodeDict,
        ...nodeData,
        original_node_id: nodeId, // Match Python's logic of renaming 'id' to 'original_node_id'
    };

    // Instantiate the correct node type based on the 'type' field
    switch (nodeType) {
        case 'start':
            return new StartNode(nodeArgs);
        case 'human':
            return new HumanNode(nodeArgs);
        case 'agent':
            return new AgentNode(nodeArgs);
        case 'retriever':
            return new RetrieverNode(nodeArgs);
        case 'memory_interrupt':
            return new MemoryInterruptNode(nodeArgs);
        case 'llm':
            return new LLMNode(nodeArgs);
        case 'requirement_category':
            return new RequirementCategoryNode(nodeArgs);
        case 'condition_branch':
            return new ConditionBranchNode(nodeArgs);
        case 'http_request':
            return new HttpRequestNode(nodeArgs);
        case 'custom_code':
            return new CustomCodeNode(nodeArgs);
        case 'template_conversion':
            return new TemplateConversionNode(nodeArgs);
        case 'variable_aggregation':
            return new VariableAggregationNode(nodeArgs);
        case 'constant_variable':
            return new ConstantVariableNode(nodeArgs);
        case 'tool':
            return new ToolNode(nodeArgs);
        case 'skill':
            return new SkillNode(nodeArgs);
        case 'end':
            return new EndNode(nodeArgs);
        default:
            throw new Error(`Unknown node type: ${nodeType}`);
    }
}

/**
 * Creates a collection of node objects from an array of objects.
 * Each object in the array represents a node, and this function
 * uses the createNodeFromObject function to create each node instance
 * based on the node type specified in the object.
 *
 * @param {Object[]} nodesDict - An array of objects, each representing a node.
 * @returns {Nodes} An instance of the Nodes class containing node objects.
 */
function createNodesFromObject(nodesDict) {
    const nodes = new Nodes();
    nodesDict.forEach(nodeDict => {
        const node = createNodeFromObject(nodeDict);
        nodes.addNode(node);
    });
    return nodes;
}

export { createNodeFromObject, createNodesFromObject };
