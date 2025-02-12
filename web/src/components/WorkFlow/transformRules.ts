/*
 * @LastEditors: biz
 */
import { BlockEnum, NodeTypeTransformRules } from './types';

// Define transform rules for TaskExecution node
const taskExecutionRules = {
    handles: [
        {
            handleId: 'executor_list',
            transform: (sourceNode) => ({
                currentId: sourceNode.id,
                isChild: true
            })
        }
    ]
};

// Rules for each node type
export const transformRules: NodeTypeTransformRules = {
    [BlockEnum.TaskExecution]: taskExecutionRules,
    // Add rules for other node types as needed
}; 