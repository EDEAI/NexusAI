/*
 * @LastEditors: biz
 */
import { useIntl } from '@umijs/max';
import { ReactFlow, getOutgoers, reconnectEdge } from '@xyflow/react';
import { useUpdateEffect } from 'ahooks';
import { message } from 'antd';
import { memo, useCallback } from 'react';
import { ReactFlowProvider } from 'react-flow-renderer';
import useStore from './store';
import { BlockEnum } from './types';
type WorkflowProviderProps = {
    children: React.ReactNode;
};
const selector = state => ({
    nodes: state.nodes,
    edges: state.edges,
    onNodesChange: state.onNodesChange,
    onEdgesChange: state.onEdgesChange,
    onConnect: state.onConnect,
    nodeTypes: state.nodeTypes,
    connectionLineStyle: state.connectionLineStyle,
    defaultViewport: state.defaultViewport,
    onDrop: state.onDrop,
    onDragOver: state.onDragOver,
    setSelect: state.setSelect,
    preventScrolling: state.preventScrolling,
});

export const CustomWorkflowContextProvider = memo(({ children }: WorkflowProviderProps) => {
    // const { nodes, edges, onNodesChange, onEdgesChange, onConnect } = useStore(
    //     useShallow(selector),
    // );
    // const reactflow=useReactFlow()
    const intl = useIntl();
    const nodes = useStore(state => state.nodes);
    const getEdges = useStore(state => state.getEdges);
    const edges = useStore(state => state.edges);
    const setEdges = useStore(state => state.setEdges);
    const onNodesChange = useStore(state => state.onNodesChange);
    const onEdgesChange = useStore(state => state.onEdgesChange);
    const onConnect = useStore(state => state.onConnect);
    const nodeTypes = useStore(state => state.nodeTypes);
    const connectionLineStyle = useStore(state => state.connectionLineStyle);
    const defaultViewport = useStore(state => state.defaultViewport);
    const onDrop = useStore(state => state.onDrop);
    const onDragOver = useStore(state => state.onDragOver);
    const setSelect = useStore(state => state.setSelect);
    const preventScrolling = useStore(state => state.preventScrolling);

    const isValidConnection = useCallback(
        connection => {
            // we are using getNodes and getEdges helpers here
            // to make sure we create isValidConnection function only once
            //   const nodes = getNodes();
            //   const edges = getEdges();
            const target = nodes.find(node => node.id === connection.target);
            const hasCycle = (node, visited = new Set()) => {
                if (visited.has(node.id)) return false;

                visited.add(node.id);

                for (const outgoer of getOutgoers(node, nodes, edges)) {
                    if (outgoer.id === connection.source) return true;
                    if (hasCycle(outgoer, visited)) return true;
                }
            };

            if (target.id === connection.source) return false;
            return !hasCycle(target);
        },
        [nodes, edges],
    );
    // const {
    //     nodes,
    //     edges,
    //     onNodesChange,
    //     onEdgesChange,
    //     onConnect,
    //     nodeTypes,
    //     connectionLineStyle,
    //     defaultViewport,
    //     onDrop,
    //     onDragOver,
    //     setSelect,
    //     preventScrolling,

    // } = useStore(selector, shallow);

    const onViewportChange = () => {};
    const onReconnect = useCallback((oldEdge, newConnection) => {
        console.log(
            oldEdge,
            newConnection,
            getEdges(),
            reconnectEdge(oldEdge, newConnection, edges),
        );

        setEdges(reconnectEdge(oldEdge, newConnection, getEdges()));
    }, []);
    useUpdateEffect(() => {
        // console.log('【context:Nodes】',nodes)
    }, [nodes]);

    return (
        <ReactFlowProvider>
            <ReactFlow
                onViewportChange={onViewportChange}
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onEdgesDelete={e => {}}
                onConnect={onConnect}
                onReconnect={onReconnect}
                // selectNodesOnDrag={false}
                // style={{ background: bgColor }}
                nodeTypes={nodeTypes}
                minZoom={0.3}
                maxZoom={1}
                connectionLineStyle={connectionLineStyle}
                snapToGrid={false}
                isValidConnection={isValidConnection}
                connectionRadius={30}
                // defaultViewport={{
                //     x: 0,
                //     y: 300,
                //     zoom: 1,
                // }}
                preventScrolling={preventScrolling}
                onDragOver={onDragOver}
                onPaneClick={() => {
                    setSelect('');
                }}
                onPaneContextMenu={e => {
                    e.preventDefault();
                }}
                onSelectionChange={e => {}}
                onNodeClick={(e, element) => {
                    setSelect(element.id);
                }}
                onEdgeClick={(e, element) => {}}
                deleteKeyCode={['Delete', 'Backspace']}
                onNodesDelete={e => {}}
                onBeforeDelete={async gh => {
                    if (gh?.nodes?.[0]?.type == BlockEnum.Start) {
                        message.error(intl.formatMessage({ id: 'workflow.delStartNodeError' }));
                        return Promise.reject(
                            intl.formatMessage({ id: 'workflow.delStartNodeError' }),
                        );
                    }
                    setSelect('');
                    return Promise.resolve(gh);
                }}
                fitView

                // attributionPosition={false}
            >
                {children}
            </ReactFlow>
        </ReactFlowProvider>
    );
});
