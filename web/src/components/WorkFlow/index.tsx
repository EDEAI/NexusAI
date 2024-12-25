/*
 * @LastEditors: biz
 */
import { devLogin } from '@/api';
import {
    getAgentList,
    getSkillList,
    getToolsList,
    getVectorList,
    getWorkFlowInfo,
    publishWorkFlow,
} from '@/api/workflow';
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
import { Button, message, Modal, Typography } from 'antd';
import { memo, useEffect, useRef, useState } from 'react';
import { useIntl, useSearchParams } from 'umi';
import { CustomWorkflowContextProvider } from './context';
import useDnD from './hooks/useDnD';
import NodePanel from './NodePanel'
import './index.less';

import { PlayCircleOutlined, SyncOutlined } from '@ant-design/icons';
import DealtWith from './components/DealtWith';
import { ChildPanel, Panel } from './nodes';
import { NodeTypes } from './nodes/nodeDisperse';
import useSaveWorkFlow from './saveWorkFlow';
import useStore from './store';
import { AppNode, BlockEnum } from './types';
import Tools from './components/Tools';
import usePageVisibilityEffect from './hooks/usePageVisibilityEffect ';

const DnDFlow = () => {
    const intl = useIntl();
    const reactFlowWrapper = useRef(null);
    // const {
    //     resetNodes,
    //     setNodeTypes,
    //     addNode,
    //     setAgentData,
    //     createNode,
    //     setNodes,
    //     setEdges,
    //     setAppId,
    //     setSkillData,
    //     setToolData,
    //     setRunPanelShow,
    //     setDatasetData,
    //     getModelData,
    //     setWorkFlowInfo,
    //     setViewPort: storeSetViewPort,
    // } = useStore();
    const resetNodes = useStore(state => state.resetNodes);
    const setNodeTypes = useStore(state => state.setNodeTypes);
    const addNode = useStore(state => state.addNode);
    const setAgentData = useStore(state => state.setAgentData);
    const createNode = useStore(state => state.createNode);
    const setNodes = useStore(state => state.setNodes);
    const setEdges = useStore(state => state.setEdges);
    const setAppId = useStore(state => state.setAppId);
    const setSkillData = useStore(state => state.setSkillData);
    const setToolData = useStore(state => state.setToolData);
    const setRunPanelShow = useStore(state => state.setRunPanelShow);
    const runPanelShow = useStore(state => state.runPanelShow);
    const setDatasetData = useStore(state => state.setDatasetData);
    const setTeamDatasetData = useStore(state => state.setTeamDatasetData);
    const getModelData = useStore(state => state.getModelData);
    const setWorkFlowInfo = useStore(state => state.setWorkFlowInfo);
    const storeSetViewPort = useStore(state => state.setViewPort);
    const setHandleList = useStore(state => state.setHandleList);
    const workFlowInfo = useStore(state => state.workFlowInfo);
    const setWorkflowEditInfo = useStore(state => state.setWorkflowEditInfo);
    const [messageApi, contextHolder] = message.useMessage();
    const { screenToFlowPosition, getNodes, setViewport } = useReactFlow();
    const { onDnD } = useDnD(screenToFlowPosition);
    const [searchParams] = useSearchParams();
    const publishStatus = searchParams.get('type') == 'true';
    const nodesInitialized = useNodesInitialized({
        includeHiddenNodes: false,
    });
    const documentVisibility = useDocumentVisibility();
    const [viewPort, setViewPort] = useState(null);

    const saveWorkFlow = useSaveWorkFlow();
    const [toFn, setToFn] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [toPath, setToPath] = useState('');
    let unblock = null;
    useOnViewportChange({
        onEnd: (viewport: Viewport) => {
            // setViewPort(viewport);
            // storeSetViewPort(viewport);
        },
    });
    useMount(() => {
        setNodeTypes(NodeTypes());
        resetNodes();

        devLogin();

        init();
        setHandleList([]);
    });
    useEffect(() => {
        if (toFn) {
            history.push(toPath);
            return;
        }
        let unblock = history.block((location, action) => {
            //
            if (runPanelShow) {
                setToPath(location.location.pathname);
                setIsModalOpen(true);

                return;
            }
        });
        // setToFn(unblock)
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
            if (lastNode.data['drag']) {
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
            console.log(position, type, item);
            createNode(type, {
                position,
                data: {
                    title: item.name,
                    desc: item.description,
                    drag: true,
                    baseData: item,
                },
            });
        });
        return cleanup;
    }, [onDnD, addNode]);

    useUpdateEffect(() => {
        if (documentVisibility == 'hidden') {
            // saveFlow()
            saveWorkFlow();
        }
    }, [documentVisibility]);

    // usePageVisibilityEffect({
    //     onBeforeUnload: (event) => {

    //         saveWorkFlow();
    //
    //     },
    // });

    const init = async () => {
        const appId = searchParams.get('app_id');
        if (publishStatus) {
            messageApi.open({
                type: 'warning',
                content: intl.formatMessage({ id: 'workflow.nodeRunOtherMessage' }),
                duration: 10,
            });
        }
        setAppId(appId);
        getWorkFlowInfo(appId, publishStatus ? 1 : 0).then(res => {
            if (res.code == 0) {
                setWorkFlowInfo({
                    ...res.data,
                    isProd: publishStatus,
                });
                if (!res.data.workflow.graph) {
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
                } else {
                }
            }
        });
        getAgentList(2).then(res => {
            if (res.code == 0) {
                setAgentData({ team: res.data });
            }
        });

        getAgentList(3).then(res => {
            if (res.code == 0) {
                setAgentData({ user: res.data });
            }
        });

        getSkillList(2).then(res => {
            if (res.code == 0) {
                setSkillData({ team: res.data });
            }
        });
        getSkillList(3).then(res => {
            if (res.code == 0) {
                setSkillData({ user: res.data });
            }
        });
        getToolsList().then(res => {
            if (res.code == 0) {
                setToolData({
                    list: Object.values(res.data),
                });
            }
        });
        getModelData();
        getVectorList().then(res => {
            if (res.code == 0) {
                setDatasetData({
                    list: res.data.data.map(x => {
                        return {
                            ...x,
                            label: x.name,
                            value: x.dataset_id,
                        };
                    }),
                });
            }
        });
        getVectorList(2).then(res => {
            if (res.code == 0) {
                setTeamDatasetData({
                    list: res.data.data.map(x => {
                        return {
                            ...x,
                            label: x.name,
                            value: x.dataset_id,
                        };
                    }),
                });
            }
        });
    };

    const runFlow = () => {
        setRunPanelShow(true);
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
                    defaultMessage: '，?',
                })}
            </Modal>
            <div className="reactflow-wrapper" ref={reactFlowWrapper}>
                <CustomWorkflowContextProvider>
                    <Background></Background>
                     
                    <div>
                        <MiniMap
                            className="table"
                            nodeColor={'#1890ff'}
                            position="bottom-left"
                            maskStrokeWidth={3}
                            pannable
                            nodeStrokeWidth={3}
                        ></MiniMap>
                    </div>
                </CustomWorkflowContextProvider>
            </div>
            <div className="fixed left-8 top-16 flex  flex-col gap-2 pt-3 pl-4">
             
                <Typography.Title className="!m-0" level={5}>
                    {workFlowInfo?.app?.name}
                </Typography.Title>
                {publishStatus && (
                    <Typography.Text>
                        ( {intl.formatMessage({ id: 'workflow.nodeRunOtherMessage' })})
                    </Typography.Text>
                )}
                <Typography.Text>{workFlowInfo?.app?.description}</Typography.Text>
            </div>
            <NodePanel></NodePanel>
            <Tools />


            {/* <CreateWorkflowPanel /> */}
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
