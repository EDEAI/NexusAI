/*
 * @LastEditors: biz
 */
import { BlockEnum, NodeTypeRules, Connection, AppNode } from './types';

// Define rules for TaskExecution node
const taskExecutionRules = {
    handles: {
        'executor_list': {
            // Connection validation
            validate: (connection, nodes) => {
                const sourceNode = nodes.find(node => node.id === connection.source);
                return sourceNode?.type === BlockEnum.LLM || sourceNode?.type === BlockEnum.Agent;
            },
            errorMessage: 'Only LLM or Agent nodes can be connected to executor_list',
            
            // Transform logic
            transform: (sourceNode) => ({
                currentId: sourceNode.id,
                isChild: true
            })
        }
        // Add other handles as needed
    }
};

// Rules for each node type
export const nodeRules: NodeTypeRules = {
    [BlockEnum.TaskExecution]: taskExecutionRules,
    // Add rules for other node types as needed
};

// Helper functions
export function validateConnection(connection: Connection, nodes: AppNode[]): boolean {
    const targetNode = nodes.find(node => node.id === connection.target);
    const rules = nodeRules[targetNode?.type];
    const handleRule = rules?.handles[connection.targetHandle];
    
    return handleRule?.validate ? handleRule.validate(connection, nodes) : true;
}

export function getTransform(nodeType: BlockEnum, handleId: string) {
    return nodeRules[nodeType]?.handles[handleId]?.transform;
}

export function isSpecialHandle(handleId: string): boolean {
    return Object.values(nodeRules).some(typeRules => 
        Object.keys(typeRules.handles).includes(handleId)
    );
}