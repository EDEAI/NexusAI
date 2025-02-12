import { BlockEnum, NodeConnectionRules, NodeTypeConnectionRules } from './types';

// Define rules for TaskExecution node
const taskExecutionRules: NodeConnectionRules = {
    'executor_list': {
        validate: (connection, nodes) => {
            const sourceNode = nodes.find(node => node.id === connection.source);
            return sourceNode?.type === BlockEnum.LLM || sourceNode?.type === BlockEnum.Agent;
        },
        errorMessage: 'Only LLM or Agent nodes can be connected to executor_list'
    }
};

// Rules for each node type
export const connectionRules: NodeTypeConnectionRules = {
    [BlockEnum.TaskExecution]: taskExecutionRules,
    // Add rules for other node types as needed
}; 