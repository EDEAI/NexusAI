// Importing necessary modules
import { v4 as uuidv4 } from 'uuid';

export class Edge {
    /**
     * Represents an edge in the workflow, connecting two nodes.
     *
     * @param {number} level - The level of the edge in the workflow.
     * @param {string} source_node_id - The ID of the source node of the edge.
     * @param {string} target_node_id - The ID of the target node the edge points to.
     * @param {string} source_node_type - The type of the source node.
     * @param {string} target_node_type - The type of the target node.
     * @param {boolean} is_logical_branch - Indicates whether the edge is part of a logical branch.
     * @param {string} [condition_id] - An optional identifier for conditions matching the source node's output.
     * @param {Object} views - Data required for the web.
     * @param {string} [original_edge_id] - The original ID of the edge if it has been recreated or duplicated. Optional.
     */
    constructor({
        level,
        source_node_id,
        target_node_id,
        source_node_type,
        target_node_type,
        is_logical_branch,
        condition_id = undefined,
        views = {},
        original_edge_id = null,
    }) {
        this.id = original_edge_id || uuidv4();
        this.level = level;
        this.source_node_id = source_node_id;
        this.target_node_id = target_node_id;
        this.source_node_type = source_node_type;
        this.target_node_type = target_node_type;
        this.is_logical_branch = is_logical_branch;
        if (condition_id !== undefined) {
            this.condition_id = condition_id;
        }
        this.views = views;
    }
    /**
     * Converts the Edge object to a plain object.
     *
     * @returns {Object} A plain object representation of the Edge instance.
     */
    toObject() {
        const obj = {
            id: this.id,
            level: this.level,
            source_node_id: this.source_node_id,
            target_node_id: this.target_node_id,
            source_node_type: this.source_node_type,
            target_node_type: this.target_node_type,
            is_logical_branch: this.is_logical_branch,
            views: this.views,
        };
        if (this.condition_id !== undefined) {
            obj.condition_id = this.condition_id;
        }
        return obj;
    }
}

export class Edges {
    /**
     * Represents a collection of Edge instances in a workflow.
     */
    constructor() {
        this.edges = [];
    }

    /**
     * Adds an Edge instance to the collection.
     *
     * @param {Edge} edge - The Edge instance to be added.
     */
    addEdge(edge) {
        this.edges.push(edge);
    }

    /**
     * Converts the collection of Edge instances to an array of plain objects.
     *
     * @returns {Object[]} An array of plain objects, each representing an Edge instance.
     */
    toObject() {
        return this.edges.map(edge => edge.toObject());
    }

    /**
     * Builds mappings of nodes to their incoming and outgoing edges.
     *
     * @returns {Object} A dictionary containing two dictionaries:
     *                   - 'incoming': Maps node IDs to lists of incoming edges.
     *                   - 'outgoing': Maps node IDs to lists of outgoing edges.
     */
    buildEdgeMaps() {
        const nodeToIncomingEdges = {};
        const nodeToOutgoingEdges = {};

        for (const edge of this.edges) {
            if (!nodeToOutgoingEdges[edge.source_node_id]) {
                nodeToOutgoingEdges[edge.source_node_id] = [];
            }
            nodeToOutgoingEdges[edge.source_node_id].push(edge);

            if (!nodeToIncomingEdges[edge.target_node_id]) {
                nodeToIncomingEdges[edge.target_node_id] = [];
            }
            nodeToIncomingEdges[edge.target_node_id].push(edge);
        }

        return {
            incoming: nodeToIncomingEdges,
            outgoing: nodeToOutgoingEdges,
        };
    }

    /**
     * Recursively finds all ancestor node IDs for a given node ID.
     *
     * @param {string} nodeId - The ID of the node to find ancestors for.
     * @returns {string[]} A list of all ancestor node IDs.
     */
    getAllAncestorNodeIds(nodeId) {
        const ancestorNodeIds = [];

        const findAncestors = currentNodeId => {
            for (const edge of this.edges) {
                if (edge.target_node_id === currentNodeId) {
                    if (!ancestorNodeIds.includes(edge.source_node_id)) {
                        ancestorNodeIds.push(edge.source_node_id);
                        findAncestors(edge.source_node_id);
                    }
                }
            }
        };

        findAncestors(nodeId);
        return ancestorNodeIds;
    }
}

/**
 * Creates an Edge instance from a plain object representation.
 *
 * @param {Object} edge_obj - A plain object representing an Edge instance.
 * @returns {Edge} An Edge instance created from the plain object.
 */
function createEdgeFromObject(edge_obj) {
    return new Edge(
        edge_obj.level,
        edge_obj.source_node_id,
        edge_obj.target_node_id,
        edge_obj.source_node_type,
        edge_obj.target_node_type,
        edge_obj.is_logical_branch,
        edge_obj.condition_id, // Optional, may be undefined
        edge_obj.views,
        edge_obj.id, // Assuming 'id' is the property for original_edge_id
    );
}

/**
 * Creates an Edges instance from an array of plain objects.
 *
 * @param {Object[]} edge_obj_array - An array of plain objects representing Edge instances.
 * @returns {Edges} An Edges instance containing Edge instances created from the array of plain objects.
 */
export function createEdgesFromList(edge_obj_array) {
    const edges = new Edges();
    edge_obj_array.forEach(edge_obj => {
        edges.addEdge(createEdgeFromObject(edge_obj));
    });
    return edges;
}
