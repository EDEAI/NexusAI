/*
 * @LastEditors: biz
 */
import { devLogin } from '@/api';
import { getWorkFlowInfo } from '@/api/workflow';
import { history } from '@umijs/max';
import {
    Background,
    MiniMap,
    ReactFlowProvider,
    useNodesInitialized,
    useOnViewportChange,
    useReactFlow,
    Viewport,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useDocumentVisibility, useMount, useUpdateEffect } from 'ahooks';
import { message, Modal } from 'antd';
import { memo, useEffect, useRef, useState } from 'react';
import { useIntl, useSearchParams } from 'umi';
import { CustomWorkflowContextProvider } from './context';
import useDnD from './hooks/useDnD';
import useFetchData from './hooks/useFetchData'; // 引入自定义的hooks

import './index.less';

import DealtWith from './components/DealtWith';
import NodePanel from './components/NodePanel';
import Tools from './components/Tools';
import { ChildPanel, Panel } from './nodes';
import { NodeTypes } from './nodes/nodeDisperse';
import useSaveWorkFlow from './saveWorkFlow';
import useStore from './store';
import { AppNode, BlockEnum } from './types';
// import usePageVisibilityEffect from './hooks/usePageVisibilityEffect';

const DnDFlow = () => {
    const intl = useIntl();
    const reactFlowWrapper = useRef(null);
    const resetNodes = useStore(state => state.resetNodes);
    const setNodeTypes = useStore(state => state.setNodeTypes);
    const addNode = useStore(state => state.addNode);
    const createNode = useStore(state => state.createNode);
    const setNodes = useStore(state => state.setNodes);
    const setEdges = useStore(state => state.setEdges);
    const setAppId = useStore(state => state.setAppId);
    const setRunPanelShow = useStore(state => state.setRunPanelShow);
    const runPanelShow = useStore(state => state.runPanelShow);
    const getModelData = useStore(state => state.getModelData);
    const setWorkFlowInfo = useStore(state => state.setWorkFlowInfo);
    const setHandleList = useStore(state => state.setHandleList);
    const workFlowInfo = useStore(state => state.workFlowInfo);
    const setWorkflowEditInfo = useStore(state => state.setWorkflowEditInfo);
    const [messageApi, contextHolder] = message.useMessage();
    const { screenToFlowPosition, getNodes, setViewport } = useReactFlow();
    const { onDnD } = useDnD(screenToFlowPosition);
    const [searchParams] = useSearchParams();
    const publishStatus = searchParams.get('type') == 'true';
 
    const setLoadingWorkflowData = useStore(state => state.setLoadingWorkflowData);
    const nodesInitialized = useNodesInitialized({
        includeHiddenNodes: false,
    });
    const documentVisibility = useDocumentVisibility();

    const saveWorkFlow = useSaveWorkFlow();
    const [toFn, setToFn] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [toPath, setToPath] = useState('');
    let unblock = null;
    useOnViewportChange({
        onEnd: (viewport: Viewport) => {
            // setViewPort(viewport);
        },
    });

    useMount(() => {
        setNodeTypes(NodeTypes());
        resetNodes();
        devLogin();
        init();
        setHandleList([]);
    });

    useFetchData(); // 使用自定义的hooks获取数据

    useEffect(() => {
        if (toFn) {
            history.push(toPath);
            return;
        }
        let unblock = history.block((location, action) => {
            if (runPanelShow) {
                setToPath(location.location.pathname);
                setIsModalOpen(true);
                return;
            }
        });

        if (!runPanelShow) {
            unblock?.();
        }

        return () => {
            unblock?.();
        };
    }, [runPanelShow, toFn]);

    useUpdateEffect(() => {
        if (nodesInitialized) {
            const allNodes = getNodes();
            const lastNode = allNodes[allNodes.length - 1];
            if (lastNode?.data['drag']) {
                lastNode.position = {
                    x: lastNode.position.x - lastNode.measured.width / 2,
                    y: lastNode.position.y - lastNode.measured.height / 2,
                };
                setNodes(allNodes as AppNode[]);
            }
        }
    }, [nodesInitialized]);

    useEffect(() => {
        const cleanup = onDnD((position: { x: number; y: number }, type, item) => {
         
            const createData={
                // title: item.name,
                // desc: item.description,
                drag: true,
                ...item.data,
                baseData: item.baseData,
                // outputInfo: item?.baseData?.output,
            }
            if(item.baseData?.output){
                createData.outputInfo = item.baseData?.output;
            }
            
            createNode(type, {
                position,
                data:createData ,
            });
            
        });
        
        return cleanup;
    }, [onDnD, addNode]);

    useUpdateEffect(() => {
        if (documentVisibility == 'hidden') {
            saveWorkFlow();
        }
    }, [documentVisibility]);

    const init = async () => {
        const appId = searchParams.get('app_id');
        if (publishStatus) {
            messageApi.open({
                type: 'warning',
                content: intl.formatMessage({ id: 'workflow.nodeRunOtherMessage' }),
                duration: 10,
            });
        }
        setLoadingWorkflowData(true);
        setAppId(appId);
        getWorkFlowInfo(appId, publishStatus ? 1 : 0).then(res => {
            if (res.code == 0&&res.data) {
                setWorkFlowInfo({
                    ...res.data,
                    isProd: publishStatus,
                });
                if (!res.data.workflow.graph) {
                    setLoadingWorkflowData(false);
                    createNode(BlockEnum.Start);
                    return;
                }
                const {
                    workflow: {
                        graph: { edges, nodes, views },
                    },
                    app,
                } = res.data;
                setWorkflowEditInfo({
                    enable_api: !!app.enable_api,
                    is_public: !!app.is_public,
                });
                views?.nodes && setNodes(views.nodes);
                views?.edges && setEdges(views.edges);
                if (views?.viewPort) {
                    // setViewport(views.viewPort);
                }
                setTimeout(() => {
                    setLoadingWorkflowData(false);
                }, 1000);
            }
        });
        getModelData();
    };

    const handleOk = () => {
        setToFn(true);
        console.log(toPath);

        history.push(toPath);
        setIsModalOpen(false);
    };
    const handleCancel = () => {
        setIsModalOpen(false);
    };
    return (
        <div className="dndflow">
            {contextHolder}
            <Modal
                title={intl.formatMessage({ id: 'workflow.modal.title', defaultMessage: '' })}
                open={isModalOpen}
                onOk={handleOk}
                onCancel={handleCancel}
            >
                {intl.formatMessage({
                    id: 'workflow.modal.content',
                    defaultMessage: '',
                })}
            </Modal>
            <div className="reactflow-wrapper" ref={reactFlowWrapper}>
                <CustomWorkflowContextProvider>
                    <Background></Background>
                    <div>
                        <MiniMap
                            className="table"
                            nodeColor={'#1890ff'}
                            position="bottom-right"
                            maskStrokeWidth={3}
                            pannable
                            nodeStrokeWidth={3}
                        ></MiniMap>
                    </div>
                </CustomWorkflowContextProvider>
            </div>
            <NodePanel
                // visibleTabs={['node', 'agent', 'skill', 'tool']}
                workflowName={workFlowInfo?.app?.name}
                workflowDesc={workFlowInfo?.app?.description}
                publishStatus={publishStatus}
            />
            <Tools />
            <Panel></Panel>
            <ChildPanel></ChildPanel>
            <DealtWith></DealtWith>
        </div>
    );
};

export default memo(() => (
    <ReactFlowProvider>
        <DnDFlow />
    </ReactFlowProvider>
));
