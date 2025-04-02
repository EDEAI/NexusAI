/*
 * @LastEditors: biz
 */
import { useReactFlow } from '@xyflow/react';
import dagre from 'dagre';
import { AppNode } from '../types';

const NODE_WIDTH = 200;
const NODE_HEIGHT = 80;
const LAYOUT_OPTIONS = {
  rankdir: 'TB', // 'TB' - Top to Bottom, 'LR' - Left to Right
  align: 'UL', // Align nodes
  ranker: 'longest-path', // Options: 'network-simplex', 'tight-tree', 'longest-path'
  nodesep: 80, // Horizontal spacing between nodes
  ranksep: 100, // Vertical spacing between levels
  edgesep: 10, // Spacing between edges
  marginx: 20, // Horizontal margin of the graph
  marginy: 20, // Vertical margin of the graph
};

/**
 * Auto layout implementation using dagre library
 */
const useAutoLayout = () => {
  const { getNodes, getEdges, setNodes } = useReactFlow();

  const getNodeDimensions = (node: AppNode) => {
    return {
      width: node.width || NODE_WIDTH,
      height: node.height || NODE_HEIGHT,
    };
  };

  /**
   * Execute auto layout for nodes
   * @param direction Layout direction, 'TB' - Top to Bottom, 'LR' - Left to Right
   */
  const autoLayout = (direction: 'TB' | 'LR' = 'TB') => {
    const nodes = getNodes();
    const edges = getEdges();
    
    if (!nodes.length) return;

    // Create a new dagre graph instance
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    
    // Set layout direction
    const layoutOptions = {
      ...LAYOUT_OPTIONS,
      rankdir: direction,
    };
    
    dagreGraph.setGraph(layoutOptions);

    // Add nodes to the dagre graph
    nodes.forEach((node) => {
      const { width, height } = getNodeDimensions(node as AppNode);
      dagreGraph.setNode(node.id, { width, height });
    });

    // Add edges to the dagre graph
    edges.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target);
    });

    // Run the layout algorithm
    dagre.layout(dagreGraph);

    // Apply layout results to nodes
    const layoutedNodes = nodes.map((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      
      return {
        ...node,
        position: {
          x: nodeWithPosition.x - (nodeWithPosition.width / 2),
          y: nodeWithPosition.y - (nodeWithPosition.height / 2),
        },
      };
    });

    // Update node positions
    setNodes(layoutedNodes);
  };

  return { autoLayout };
};

export default useAutoLayout; 