/*
 * @LastEditors: biz
 */
import { getModelList } from '@/api/workflow';
import { Edge, Edges } from '@/py2js/edges.js';
import { Nodes } from '@/py2js/nodes/base.js';
import { Variable } from '@/py2js/variables.js';
import { addEdge, applyEdgeChanges, applyNodeChanges } from '@xyflow/react';
import _ from 'lodash';
import { v4 as uuid } from 'uuid';
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { EDGE_COLOR } from './config';
import { getBaseNode } from './nodes/nodeDisperse';
import { transformer } from './transformWrokFlow';
import { AppNode, AppState, BlockEnum, NodeCreate } from './types';
import { customFreeNode } from './utils/createNode';
import { connectionRules } from './connectionRules';
import { transformRules, NodeTypeTransformRules } from './transformRules';
let lastSelect = '';

// this is our useStore hook that we can use in our components to get parts of the store and call actions
const useStore = create(
    devtools<AppState>(
        (set, get) => ({
            workFlowInfo: {},
            nodes: [],
            freeNodes: new Nodes(),
            edges: [],
            selectedNode: null,
            showChildNode: null,
            agentData: {},
            preventScrolling: true,
            app_id: '',
            skillData: {},
            toolData: {},
            datasetData: {},
            teamDatasetData: {},
            modelData: {},
            modelOptionsData:{},
            dealtWithData: null,
            runPanelShow: false,
            runPanelNodeShow: false,
            viewport: { x: 0, y: 0, zoom: 1 },
            handleList: [],
            workflowEditInfo: {},
            setModelOptionsData: data => {
                set({ modelOptionsData: data });
            },
            getNode(id) {
                return get().nodes.find(x => x.id == id);
            },

            setShowChildNode: node => {
                set({ showChildNode: node });
            },
            setWorkflowEditInfo: data => {
                set({ workflowEditInfo: data });
            },
            setDealtWithData: data => {
                set({ dealtWithData: data });
            },
            setViewPort: viewport => {
                set({ viewport });
            },
            setRunPanelShow: show => {
                set({ runPanelShow: show });
            },
            setRunPanelNodeShow: show => {
                set({ runPanelNodeShow: show });
            },
            addHandleList: list => {
                set({ handleList: [...get().handleList, ...list] });
            },
            setHandleList: list => {
                set({ handleList: list });
            },

            //  nodes  setNodes
            onNodesChange: changes => {
                const updatedNodes = applyNodeChanges(changes, get().nodes);
                set({ nodes: updatedNodes });

                // return updatedNodes; //  nodes
            },
            async getModelData() {
                if (!_.isEmpty(get().modelData)) {
                    return get().modelData.list;
                }
                const res = await getModelList();
                if (res.code == 0) {
                    const result = res.data.data.map(x => {
                        return {
                            ...x,
                            label: x.model_name,
                            value: x.model_config_id,
                        };
                    });
                    set({
                        modelData: {
                            list: result,
                        },
                    });
                    return result;
                }
            },
            setWorkFlowInfo(data) {
                set({ workFlowInfo: data });
            },
            setDatasetData(data) {
                set({ datasetData: { ...get().datasetData, ...data } });
            },
            setTeamDatasetData(data) {
                set({ teamDatasetData: { ...get().teamDatasetData, ...data } });
            },
            setSkillData(data) {
                set({ skillData: { ...get().skillData, ...data } });
            },
            setPreventScrolling: value => {
                set({ preventScrolling: value });
            },
            setToolData(data) {
                set({ toolData: { ...get().toolData, ...data } });
            },
            setAgentData: data => {
                set({ agentData: { ...get().agentData, ...data } });
            },
            setAppId: app_id => {
                set({ app_id });
            },
            getEdges() {
                return get().edges;
            },
            getInputVariables(nodeId) {
                const node = get().nodes.find(x => x.id == nodeId);
                if (!node) return null;
                const handle = transformer[node.type]?.handle;
                const freeNode = handle?.(node);
                if (!freeNode) {
                    return null;
                }
                const getContext = transformer[node.type]?.context;
                console.log('freeNode', freeNode);

                const context = getContext?.(freeNode);
                if (!context) {
                    return null;
                }

                return context;
            },
            transformWorkFlow() {
                const { nodes, edges } = get().flowSetLevel();
                const freeNodes = new Nodes();
                
                // First pass: Find all special handle nodes
                const specialHandleNodes = new Map();
                edges.forEach(edge => {
                    const targetNode = nodes.find(node => node.id === edge.target);
                    const sourceNode = nodes.find(node => node.id === edge.source);
                    
                    // Get transform rules for target node type
                    const nodeRules = transformRules[targetNode?.type];
                    if (nodeRules?.handles) {
                        // Find matching handle rule
                        const handleRule = nodeRules.handles.find(rule => 
                            rule.handleId === edge.targetHandle
                        );
                        
                        if (handleRule && sourceNode) {
                            if (!specialHandleNodes.has(targetNode.id)) {
                                specialHandleNodes.set(targetNode.id, new Map());
                            }
                            
                            const handleMap = specialHandleNodes.get(targetNode.id);
                            if (!handleMap.has(handleRule.handleId)) {
                                handleMap.set(handleRule.handleId, []);
                            }
                            
                            // Transform and add source node
                            const transformedNode = {
                                ...sourceNode,
                                ...handleRule.transform(sourceNode)
                            };
                            handleMap.get(handleRule.handleId).push(transformedNode);
                        }
                    }
                });

                // Second pass: Transform nodes
                const newNodes = nodes.map(node => {
                    const handle = transformer[node.type]?.handle;
                    if (!handle) {
                        return node;
                    }

                    // Check if node has special handles
                    if (specialHandleNodes.has(node.id)) {
                        const handleMap = specialHandleNodes.get(node.id);
                        const nodeWithHandles = {
                            ...node,
                            data: {
                                ...node.data,
                                selected: false,
                            }
                        };
                        
                        // Add all special handle data
                        handleMap.forEach((nodes, handleId) => {
                            nodeWithHandles.data[handleId] = nodes;
                        });
                        
                        const freeNode = handle(nodeWithHandles);
                        freeNodes.addNode(freeNode);
                        return nodeWithHandles;
                    }

                    // Normal node handling
                    if (!isNodeInSpecialHandles(node.id, specialHandleNodes)) {
                        const freeNode = handle(node);
                        freeNodes.addNode(freeNode);
                    }
                    
                    return {
                        ...node,
                        data: {
                            ...node.data,
                            selected: false,
                        },
                    };
                }) as AppNode[];

                // Handle edges
                const freeEdges = new Edges();
                const newEdges = edges
                    .filter(edge => !isSpecialHandle(edge.targetHandle, transformRules))
                    .map(edge => {
                        const edgeParams = {
                            level: edge.level,
                            source_node_id: edge.source,
                            target_node_id: edge.target,
                            source_node_type: edge.sourceType,
                            target_node_type: edge.targetType,
                            is_logical_branch: edge.is_logical_branch,
                            condition_id: null,
                            original_edge_id: edge.id,
                        };
                        if (edge.is_logical_branch) {
                            if (edge.sourceType == BlockEnum.ConditionBranch) {
                                const sourceFreeNode = freeNodes.nodes.find(x => x.id == edge.source);
                                console.log(sourceFreeNode, edge);
                                if (edge.sourceHandle == 'start_source_else') {
                                    const id = sourceFreeNode?.data?.logic_branches?.else_branch?.id;
                                    if (id) {
                                        edgeParams.condition_id = id;
                                    }
                                } else {
                                    const id =
                                        sourceFreeNode?.data?.logic_branches?.branches[
                                            edge.sourceHandle
                                        ]?.id;
                                    console.log(111, id);

                                    if (id) {
                                        edgeParams.condition_id = id;
                                    }
                                }
                            }
                            if (edge.sourceType == BlockEnum.RequirementCategory) {
                                const sourceFreeNode = freeNodes.nodes.find(x => x.id == edge.source);
                                console.log(edge, sourceFreeNode);
                                const id =
                                    sourceFreeNode?.data?.requirement_category?.categories[
                                        edge.sourceHandle
                                    ]?.id;
                                if (id) {
                                    edgeParams.condition_id = id;
                                }
                            }
                            console.log(edge);
                        }
                        const edgeObj = new Edge(edgeParams);
                        freeEdges.addEdge(edgeObj);
                        return edgeObj;
                    });

                return {
                    freeNodes,
                    freeEdges,
                    nodes: newNodes,
                    edges
                };
            },
            flowSetLevel() {
                const { nodes, edges } = get();

                const nodeLevels = {};
                const incomingEdgesCount = {};

                nodes.forEach(node => {
                    nodeLevels[node.id] = 0;
                    incomingEdgesCount[node.id] = 0;
                });

                edges.forEach(edge => {
                    if (incomingEdgesCount.hasOwnProperty(edge.target)) {
                        incomingEdgesCount[edge.target]++;
                    }
                });

                const roots = nodes.filter(node => incomingEdgesCount[node.id] === 0);
                const queue = [...roots];

                while (queue.length > 0) {
                    const currentNode = queue.shift();
                    const currentLevel = nodeLevels[currentNode.id];

                    edges.forEach(edge => {
                        if (edge.source === currentNode.id) {
                            const targetNode = nodes.find(node => node.id === edge.target);
                            const targetNodeId = targetNode.id;

                            nodeLevels[targetNodeId] = currentLevel + 1;
                            incomingEdgesCount[targetNodeId]--;

                            if (incomingEdgesCount[targetNodeId] === 0) {
                                queue.push(targetNode);
                            }
                        }
                    });
                }

                const newNodes = nodes.map(node => {
                    const nodeLevel = nodeLevels[node.id] || 0;
                    node.level = nodeLevel;
                    return node;
                });

                const newEdges = edges.map(edge => {
                    const sourceNode = nodes.find(node => node.id === edge.source);
                    const targetNode = nodes.find(node => node.id === edge.target);
                    const sourceLevel = nodeLevels[edge.source] || 0;
                    const targetLevel = nodeLevels[edge.target] || 0;
                    const edgeLevel = Math.min(sourceLevel, targetLevel);
                    const edgeData = {
                        ...edge,
                        level: edgeLevel + 1,
                        sourceType: sourceNode ? sourceNode?.type : null,
                        targetType: targetNode ? targetNode?.type : null,
                        is_logical_branch: false,
                        condition_id: null,
                    };
                    if (sourceNode?.type == BlockEnum.ConditionBranch) {
                        edgeData.is_logical_branch = true;
                        edgeData.condition_id = sourceNode.id;
                    } else if (sourceNode?.type == BlockEnum.RequirementCategory) {
                        edgeData.is_logical_branch = true;
                        edgeData.condition_id = sourceNode.id;
                    }
                    return edgeData;
                });

                function getNodeLevel(nodeLevels, nodeId) {
                    if (!nodeLevels.hasOwnProperty(nodeId)) {
                        return null;
                    }

                    return nodeLevels[nodeId] || 0;
                }

                function getEdgeLevel(edges, nodeLevels, edgeId) {
                    const edge = edges.find(edge => edge.id === edgeId);
                    if (!edge) {
                        return null;
                    }

                    const sourceLevel = nodeLevels[edge.source] || 0;
                    const targetLevel = nodeLevels[edge.target] || 0;
                    return Math.max(sourceLevel, targetLevel);
                }

                return {
                    nodes: newNodes,
                    edges: newEdges.sort((a, b) => a.level - b.level),
                    getNodeLevel: nodeId => getNodeLevel(nodeLevels, nodeId),
                    getEdgeLevel: edgeId => getEdgeLevel(edges, nodeLevels, edgeId),
                };
            },

            getOutputVariables(nodeId, variable) {
                const { connectedNodes } = get().getAllConnectedElements(nodeId, 'target');

                const variables = connectedNodes.flatMap(node => {
                    const {
                        id,
                        type,
                        data: { title, outputInfo },
                    } = node;
                    if (!outputInfo) {
                        return [];
                    }
                    let createVar = null;
                    if (outputInfo.base) {
                        createVar = {
                            [outputInfo.key]: new Variable(outputInfo.key, 'string'),
                        };
                    } else {
                        createVar = transformer[node.type]?.variables?.(node.data) || {};
                    }

                    return createVar
                        ? Object.values(createVar).map(varObj => ({
                              title,
                              type,
                              id,
                              createVar: varObj,
                              label: `${title}.${varObj?.name}`,
                              value: `<<${id}.outputs.${varObj?.name}>>`,
                          }))
                        : [];
                });
                return variable ? variables.find(x => x.value == variable) : variables;
            },
            updateEdgeColors(nodeId, color = null) {
                const edges = get().edges;

                const connectedEdges = edges.filter(
                    edge => edge.source === nodeId || edge.target === nodeId,
                );

                const updatedEdges = edges.map(edge => {
                    if (edge.selected) return edge;
                    if (connectedEdges.find(connectedEdge => connectedEdge.id === edge.id)) {
                        return {
                            ...edge,
                            data: {
                                ...edge.data,
                                zindex: 10,
                            },
                            style: {
                                ...edge.style,
                                stroke: color || EDGE_COLOR.DEFAULT,
                                strokeWidth: color ? 2 : 1,
                            },
                        };
                    } else {
                        return {
                            ...edge,
                            data: {
                                ...edge.data,
                                zindex: 0,
                            },
                            style: {
                                ...edge.style,
                                stroke: EDGE_COLOR.DEFAULT,
                                strokeWidth: 1,
                            },
                        };
                    }
                });

                set({ edges: updatedEdges });
            },
            getAllConnectedElements(nodeId, direction = 'source') {
                const nodes = get().nodes;
                const edges = get().edges;
                const visitedNodes = new Set();
                const visitedEdges = new Set();

                function dfs(currentNodeId) {
                    if (visitedNodes.has(currentNodeId)) {
                        return;
                    }

                    visitedNodes.add(currentNodeId);

                    let connectedEdges;
                    if (direction === 'source') {
                        connectedEdges = edges.filter(edge => edge.source === currentNodeId);
                    } else if (direction === 'target') {
                        connectedEdges = edges.filter(edge => edge.target === currentNodeId);
                    }

                    connectedEdges.forEach(edge => {
                        visitedEdges.add(edge);
                        const nextNodeId = direction === 'source' ? edge.target : edge.source;
                        dfs(nextNodeId);
                    });
                }

                dfs(nodeId);

                if (nodes.find(node => node.id === nodeId)?.type != BlockEnum.Start) {
                    visitedNodes.delete(nodeId);
                }

                const connectedNodes = nodes.filter(node => visitedNodes.has(node.id));
                const connectedEdgesArray = Array.from(visitedEdges);

                return {
                    connectedNodes: connectedNodes,
                    connectedEdges: connectedEdgesArray,
                };
            },
            setSelect: (id, update = false) => {
                if (lastSelect == id && !update) return;
                lastSelect = id;
                const selectedNode = get().nodes.find(node => node.id === id);
                set({
                    nodes: get().nodes.map(node => {
                        const mergeData = {
                            ...node.data,
                            selected: id === node.id,
                        };
                        return { ...node, data: mergeData };
                    }),
                    selectedNode: selectedNode,
                });

                if (selectedNode?.type == BlockEnum.TaskExecution) {
                } else {
                    set({
                        showChildNode: null,
                    });
                }
            },
            onEdgesChange: changes => {
                const handleChanges = changes.map((x: Edge) => {
                    return x;
                });

                set({
                    edges: applyEdgeChanges(handleChanges, get().edges).map(x => {
                        return {
                            ...x,
                            style: {
                                stroke: x.selected ? EDGE_COLOR.SELECT : EDGE_COLOR.DEFAULT,
                                strokeWidth: x.selected ? 2 : 1,
                            },
                        };
                    }),
                });
            },
            onConnect: connection => {
                const targetNode = get().nodes.find(node => node.id === connection.target);
                if (!targetNode) return;

                // Get rules for target node type
                const nodeRules = connectionRules[targetNode.type];
                if (nodeRules) {
                    // Get validator for specific handle
                    const handleValidator = nodeRules[connection.targetHandle];
                    if (handleValidator) {
                        // Validate connection
                        const isValid = handleValidator.validate(connection, get().nodes);
                        if (!isValid) {
                            // Could trigger error notification here
                            return;
                        }
                    }
                }

                set({
                    edges: addEdge(
                        {
                            ...connection,
                            style: {
                                stroke: EDGE_COLOR.DEFAULT,
                                strokeWidth: 1,
                            },
                        },
                        get().edges,
                    ),
                });
            },
            resetNodes: () => {
                set({ nodes: [] });
            },
            getSelectedNode() {
                return get().nodes.find(node => node.selected);
            },
            createEdge(source, target) {},
            setNodes: nodes => {
                // console.log(nodes);
                set({ nodes });
                // set({ nodes: get().nodes.map((node) => node) });
                // console.log('Updated state nodes:', get().nodes);
            },
            createNode: (createType: NodeCreate['createType'], data?: { [key: string]: any }) => {
                let Node = getBaseNode(createType)?.base;
                if (!Node) {
                    Node = {};
                }

                const id = uuid();
                Node.id = id;
                if (data?.data) {
                    data.data = {
                        ...Node.data,
                        ...data.data,
                    };
                }
                data && (Node = { ...Node, ...data });
                get().addNode(Node);
                return Node;
            },
            addEdge(source, target) {},
            addNode: newNode => {
                const nodeFlow = customFreeNode(newNode);

                nodeFlow && get().freeNodes.addNode(nodeFlow);

                set(state => ({
                    nodes: [...state.nodes, newNode],
                    freeNodes: get().freeNodes,
                }));
            },
            updateNode: newNode => {
                const cloneNode = _.cloneDeep(newNode);
                set({
                    nodes: get().nodes.map(node => {
                        return node.id === cloneNode.id ? { ...node, ...cloneNode } : node;
                    }),
                });
            },
            updateNodeData: (nodeId, newData) => {
                const clonedNewData = _.cloneDeep(newData);
                const selectNode: AppNode = get().selectedNode;
                // if(selectNode?.id==nodeId){
                //     set({
                //         selectedNode:{
                //             ...selectNode,
                //             data:{
                //                 ...selectNode.data,
                //                 ...clonedNewData,
                //             }
                //         }
                //     })
                // }
                set({
                    nodes: get().nodes.map(node => {
                        const mergeData = {
                            ...node.data,
                            ...clonedNewData,
                        };

                        return node.id === nodeId ? { ...node, data: mergeData } : node;
                    }),
                });
            },
            updateNodeFromId: (nodeId, newNodeData) => {
                set({
                    nodes: get().nodes.map(node =>
                        node.id === nodeId ? { ...node, ...newNodeData } : node,
                    ),
                });

                // set({
                //   nodes:[...get().nodes]
                // })
                return get().nodes;
            },
            setEdges: edges => {
                set({ edges });
            },
            updateNodeColor: (nodeId, color) => {
                set({
                    nodes: get().nodes.map(node => {
                        return node;
                    }),
                });
            },

            nodeTypes: {},
            connectionLineStyle: {},
            defaultViewport: { x: 0, y: 0, zoom: 0.6 },
            onDrop: event => {},
            onInit: fn => {},
            onDragOver: event => {},
            setNodeTypes: nodeTypes => {
                set({ nodeTypes });
            },
            setConnectionLineStyle: style => {
                set({ connectionLineStyle: style });
            },
            setDefaultViewport: viewport => {
                set({ defaultViewport: viewport });
            },
            setOnDrop: onDrop => {
                set({ onDrop });
            },
            setOnDragOver: onDragOver => {
                set({ onDragOver });
            },
        }),
        { name: 'workflowStore' },
    ),
);

export default useStore;

// Helper functions
function isNodeInSpecialHandles(nodeId: string, specialHandleNodes: Map<string, Map<string, any[]>>) {
    for (const handleMap of specialHandleNodes.values()) {
        for (const nodes of handleMap.values()) {
            if (nodes.some(node => node.id === nodeId)) {
                return true;
            }
        }
    }
    return false;
}

function isSpecialHandle(handleId: string, rules: NodeTypeTransformRules): boolean {
    return Object.values(rules).some(nodeRules => 
        nodeRules.handles.some(rule => rule.handleId === handleId)
    );
}
