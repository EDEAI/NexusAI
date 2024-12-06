/*
 * @LastEditors: biz
 */
import { updateWorkFlow } from '@/api/workflow';
import { Graph } from '@/py2js/graph.js';
import { useIntl, useSearchParams } from '@umijs/max';
import { useLatest } from 'ahooks';
import { message } from 'antd';
import { useEffect } from 'react';
import useStore from './store';
import { cleanEdges } from './transformWrokFlow';
import { BlockEnum } from './types';
import useDataStore from './dataStore';

const useSaveWorkFlow = () => {
    const nodes = useStore(state => state.nodes);
    const edges = useStore(state => state.edges);
    const app_id = useStore(state => state.app_id);
    const intl = useIntl();
    const setEdges = useStore(state => state.setEdges);
    const flowSetLevel = useStore(state => state.flowSetLevel);
    const transformWorkFlow = useStore(state => state.transformWorkFlow);
    const viewPort = useStore(state => state.viewport);
    const runPanelShow = useStore(state => state.runPanelShow);
    const tempNode=useDataStore(state => state.tempNode)
    const workflowInfo = useStore(state => state.workFlowInfo);
    const workflowEditInfo = useStore(state => state.workflowEditInfo);
    const [searchParams] = useSearchParams();
    const publishStatus = searchParams.get('type') == 'true';
    const workflowEditInfoLast = useLatest(workflowEditInfo);
    const showError = (text: string) => {
        message.error(text);
    };

    useEffect(() => {}, [workflowEditInfo]);
    const save = () => {
        if (workflowInfo?.isProd) return;
        setEdges(cleanEdges(nodes, edges));
        const { edges: newEdges, nodes: newNodes } = flowSetLevel();
        console.log(newEdges, newNodes);

        const freeData = transformWorkFlow();
        console.log(freeData);
        if (freeData?.edges && freeData?.edges?.[0]?.sourceType != BlockEnum.Start) {

            return false;
        } else if (freeData?.edges && freeData.edges?.[0]?.source != freeData.nodes?.[0]?.id) {

            return false;
        }
        const graph = new Graph(freeData.freeNodes, freeData.freeEdges, {
            edges: freeData.edges,
            nodes: freeData.nodes,
            viewPort,
        });
        if (!app_id) {
            console.log('appid');
        }
        console.log(graph.toObject(), JSON.stringify(graph.toObject()));
        console.log(graph);
        const params = {
            graph: graph.toObject(),
            is_public: 1,
            enable_api: 1,
        };
        console.log(workflowEditInfoLast);

        params.is_public = +(workflowEditInfoLast?.current?.is_public || false);

        params.enable_api = +(workflowEditInfoLast?.current?.enable_api || false);

        return updateWorkFlow(app_id, params).then(res => {
            if (res?.code == 0) {
                message.success(
                    runPanelShow && res?.data?.graph_changed
                        ? intl.formatMessage({
                              id: 'workflow.message.dataUpdated',
                              defaultMessage: '，',
                          })
                        : intl.formatMessage({
                              id: 'workflow.message.saveSuccess',
                              defaultMessage: '',
                          }),
                );
                return true;
            } else {
                showError(
                    res?.message ||
                        intl.formatMessage({
                            id: 'workflow.message.saveFailure',
                            defaultMessage: '',
                        }),
                );
                return false;
            }
        });
    };
    return save;
};
export default useSaveWorkFlow;
