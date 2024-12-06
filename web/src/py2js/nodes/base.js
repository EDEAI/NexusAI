/*
 * @LastEditors: biz
 */
import { v4 as uuidv4 } from 'uuid';

// Current node id, used when the node references its own input variables
export const CURRENT_NODE_ID = '536f6e67-bcab-cbd9-cfc0-4d6172637573';

export class Node {
    /**
     * Creates a node in a workflow.
     * @param {string} type The type of the node.
     * @param {string} title The title of the node.
     * @param {string} desc A description of what the node does. Default is an empty string.
     * @param {Object} position The position of the node in the workflow, structured as: {"x": float, "y": float}.
     * @param {number} width The width of the node. Default is 0.
     * @param {number} height The height of the node. Default is 0.
     * @param {boolean} selected Indicates whether the node is selected. Default is false.
     * @param {Object} kwargs Additional keyword arguments.
     */
    constructor(kwargs) {
        const { title, desc = '', type, flow_data = {} } = kwargs;
        this.id = kwargs.original_node_id || uuidv4();
        this.data = { type, title, desc, ...kwargs };
        this.flow_data = flow_data;
    }

    /**
     * Converts the Node object to a JavaScript object.
     * @returns {Object} The Node object as a plain JavaScript object.
     */
    toObject() {
        let dataObject = {};
        for (let [k, v] of Object.entries(this)) {
            if (k.startsWith('_')) continue;
            if (k === 'data') {
                dataObject[k] = Object.fromEntries(
                    Object.entries(v).map(([kk, vv]) => [kk, vv.toObject ? vv.toObject() : vv]),
                );
            } else {
                dataObject[k] = v.toObject ? v.toObject() : v;
            }
        }
        return dataObject;
    }
}

export class Nodes {
    /**
     * Represents a collection of node objects in a workflow.
     */
    constructor() {
        this.nodes = [];
    }

    /**
     * Adds a node object to the collection.
     * @param {Node} node The node object to be added to the collection.
     */
    addNode(node) {
        this.nodes.push(node);
    }

    updateNode(node_id, newData) {
        const nodeIndex = this.nodes.findIndex(node => node.id === node_id);
        if (nodeIndex !== -1) {
            this.nodes[nodeIndex] = { ...this.nodes[nodeIndex], ...newData };
        }
        return this.nodes;
    }

    /**
     * Converts the collection of node objects to a list of JavaScript objects.
     * @returns {Object[]} A list of objects, each representing a node object.
     */
    toObject() {
        return this.nodes.map(node => node.toObject());
    }

    /**
     * Gets a node object from the collection by its ID.
     * @param {string} node_id The ID of the node object to be retrieved.
     * @returns {Node} The node object with the specified ID, or null if not found.
     */
    getNode(node_id) {
        return this.nodes.find(node => node.id === node_id) || null;
    }
}
