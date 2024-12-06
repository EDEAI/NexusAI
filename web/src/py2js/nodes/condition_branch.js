// Importing necessary modules and classes
import { v4 as uuidv4 } from 'uuid';
import { Variable, createVariableFromObject } from '../variables.js';
import { Node } from './base.js';

export class LogicCondition {
    /**
     * Represents a logical condition that compares a variable's value with a target value using a specified operator.
     * @param {Variable} variable - The variable object whose value is to be compared.
     * @param {string} operator - The operator used for comparison.
     *  When the variable is a number, includes:
     *      =
     *      ≠
     *      >
     *      <
     *      >=
     *      <=
     *      is None      (is empty)
     *      is not None  (is not empty)
     *  When the variable is a string, includes:
     *      =
     *      ≠
     *      in           (contains)
     *      not in       (does not contain)
     *      startswith   (starts with)
     *      endswith     (ends with)
     *      is None      (is empty)
     *      is not None  (is not empty)
     * @param {string} target_value - The target value to compare with the variable's value.
     */
    constructor(variable, operator, target_value) {
        if (!['string', 'number'].includes(variable.type)) {
            throw new Error(
                `Logic conditions are only supported for variables of type 'string' or 'number' (received '${variable.type}')`,
            );
        }
        this.variable = variable;
        this.operator = operator;
        this.target_value =
            variable.type === 'number' ? parseFloat(target_value) : String(target_value);
    }

    toObject() {
        return {
            variable: this.variable.toObject(),
            operator: this.operator,
            target_value: this.target_value,
        };
    }
}

export class LogicBranch {
    /**
     * Represents a list of logical conditions that are combined using logical operators ('and' or 'or') to form a conditional branch in a workflow.
     * @param {string} operator - The logical operator to apply ('and' or 'or').
     * @param {string} [original_id] - The original ID of the branch, if any.
     */
    constructor(operator, original_id = null) {
        this.id = original_id || uuidv4();
        this.conditions = [];
        this.operator = operator;
    }

    /**
     * Adds a LogicCondition instance to the list of conditions.
     * @param {LogicCondition} condition - The LogicCondition instance to add.
     */
    addCondition(condition) {
        this.conditions.push(condition);
    }

    toObject() {
        return {
            id: this.id,
            conditions: this.conditions.map(condition => condition.toObject()),
            operator: this.operator,
        };
    }
}

export class LogicBranches {
    /**
     * This class represents a series of logical branches in a workflow.
     * Each instance can contain multiple conditional branches and an optional else branch.
     *
     * @param {string} [else_branch_id] - The ID of the else branch, if it exists.
     */
    constructor(else_branch_id = null) {
        this.branches = [];
        this.else_branch = new LogicBranch('and', else_branch_id || uuidv4());
    }

    /**
     *  LogicBranch 。
     * @param {LogicBranch} branch -  LogicBranch 。
     */
    addBranch(branch) {
        this.branches.push(branch);
    }

    toObject() {
        const branchesObject = this.branches.map(branch => branch.toObject());
        branchesObject.push(this.else_branch.toObject());
        return branchesObject;
    }
}

/**
 * Creates a LogicCondition instance from an object representation.
 *
 * @param {Object} conditionObj - An object containing the properties of a LogicCondition instance.
 * @returns {LogicCondition} A LogicCondition instance populated with the provided properties.
 */
function createLogicConditionFromObject(conditionObject) {
    const variable = createVariableFromObject(conditionObject.variable);
    const operator = conditionObject.operator;
    const target_value = conditionObject.target_value;
    return new LogicCondition(variable, operator, target_value);
}

/**
 * Creates a LogicBranch instance from an object representation.
 *
 * @param {Object} branchObj - An object containing the properties of a LogicBranch instance.
 * @returns {LogicBranch} A LogicBranch instance populated with the provided properties.
 */
function createLogicBranchFromObject(branchObject) {
    const logicBranch = new LogicBranch(branchObject.operator, branchObject.id);
    branchObject.conditions.forEach(condition => {
        logicBranch.addCondition(createLogicConditionFromObject(condition));
    });
    return logicBranch;
}

/**
 * Creates a LogicBranches instance from an array of object representations.
 *
 * @param {Array<Object>} branchesArray - An array of objects, each representing a LogicBranch instance.
 * @returns {LogicBranches} A LogicBranches instance populated with the provided branches.
 */
export function createLogicBranchesFromObject(branchesList) {
    const logicBranches = new LogicBranches(branchesList[branchesList.length - 1].id);
    branchesList.slice(0, -1).forEach(branchObject => {
        logicBranches.addBranch(createLogicBranchFromObject(branchObject));
    });
    return logicBranches;
}

export class ConditionBranchNode extends Node {
    /**
     * The ConditionBranchNode object is used to create conditional branches in a workflow.
     * @param {string} title - The title of the node.
     * @param {string} [desc=""] - The description of the node.
     * @param {LogicBranches} [logic_branches=null] - The logical branches associated with the node.
     * @param {boolean} [wait_for_all_predecessors=true] - Whether to wait for all predecessor nodes before execution.
     * @param {Object} [position={}] - The position of the node.
     * @param {number} [width=0] - The width of the node.
     * @param {number} [height=0] - The height of the node.
     * @param {boolean} [selected=false] - Whether the node is selected.
     * @param {string} [original_node_id=null] - The original node ID, if any.
     */
    constructor({
        title,
        desc = '',
        logic_branches = null,
        wait_for_all_predecessors = true,
        original_node_id = null,
    }) {
        // Constructing the initialization object
        const initKwargs = {
            type: 'condition_branch',
            title,
            desc,
            logic_branches,
            wait_for_all_predecessors,
        };

        // Adding the original node ID if provided
        if (original_node_id !== null) {
            initKwargs.original_node_id = original_node_id;
        }

        // Calling the parent class constructor
        super(initKwargs);
    }
}

export default {
    ConditionBranchNode,
    LogicBranch,
    LogicBranches,
    LogicCondition,
    createLogicBranchFromObject,
    createLogicBranchesFromObject,
    createLogicConditionFromObject,
};
