/*
 * @LastEditors: biz
 */
// Importing necessary modules
import { Edges, createEdgesFromList } from './edges';
import { Nodes } from './nodes/base';
import { createNodesFromObject } from './nodes/createNodesFromObject';

/**
 * Class representing a graphical representation of a workflow, including nodes, edges, and view properties.
 */
export class Graph {
    /**
     * Initializes a new instance of the Graph class.
     *
     * @param {Nodes} nodes - An instance of the Nodes class, representing the nodes in the workflow.
     * @param {Edges} edges - An instance of the Edges class, representing the edges in the workflow.
     * @param {Object} views - Data required by the web.
     */
    constructor(nodes, edges, views) {
        this.nodes = nodes;
        this.edges = edges;
        this.views = views;
    }

    /**
     * Converts the Graph object into a plain object representation.
     *
     * @returns {Object} A plain object representing the Graph object, including nodes, edges, and view properties.
     */
    toObject() {
        console.log(this.nodes, this.nodes.toObject);

        return {
            nodes: this.nodes.toObject(),
            edges: this.edges.toObject(),
            views: this.views,
        };
    }

    /**
     * Returns the total number of steps in the workflow.
     *
     * @returns {number} The total number of steps in the workflow.
     */
    getTotalSteps() {
        return this.edges.edges.length;
    }
}

/**
 * Creates a Graph object from a plain object representation.
 *
 * @param {Object} graphObject - A plain object representing a Graph object.
 * @returns {Graph} An instance of the Graph class.
 */
function createGraphFromObject(graphObject) {
    const nodes = createNodesFromObject(graphObject.nodes);
    const edges = createEdgesFromList(graphObject.edges);
    const views = graphObject.views;
    return new Graph(nodes, edges, views);
}

// Exporting the Graph class and createGraphFromObject function for use in other modules
// export  { Graph, createGraphFromObject };
