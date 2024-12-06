/*
 * @LastEditors: biz
 */
import useScrollBarDetect from '@/hooks/useScrollBarDetect';
import { CaretRightFilled, CloseOutlined } from '@ant-design/icons';
import { ProForm, ProFormText } from '@ant-design/pro-components';
import { useIntl, useSearchParams } from '@umijs/max';
import { useReactFlow } from '@xyflow/react';
import { useLocalStorageState } from 'ahooks';
import { Button, Tooltip, Typography } from 'antd';
import _ from 'lodash';
import { memo, useCallback, useEffect, useRef } from 'react';
import { NODE_COLOR, NOT_RUN_NODE_TYPE } from '../../config';
import { useResizePanel } from '../../hooks/use-resize-panel';
import useNodeIdUpdate from '../../hooks/useNodeIdUpdate';
import useStore from '../../store';
import { AppNode, BlockEnum } from '../../types';
import RunPanelNode from '../RunPanelNode';
const { Paragraph } = Typography;

type NodeFormParams = {
    node: AppNode;
    updateNodeData: (nodeId: string, nodeData: object) => void;
};
const NodeForm = memo(({ node, updateNodeData }: NodeFormParams) => {
    const intl = useIntl();
    const formRef = useRef(null);
    const setRunPanelNodeShow = useStore(state => state.setRunPanelNodeShow);
    const setSelect = useStore(state => state.setSelect);
    const setShowChildNode = useStore(state => state.setShowChildNode);
    const showChildNode = useStore(state => state.showChildNode);
    const getNode = useStore(state => state.getNode);

    const setNodeChange = useCallback(
        (_changedValues, allValues) => {
            // updateNodeData(node?.id, allValues);
            if (node?.data?.['isChild']) {
                const parentNode = getNode(node?.id);
                const executor_list = _.cloneDeep(parentNode?.data?.executor_list);
                const editIndex = executor_list?.findIndex(x => x.currentId == node?.currentId);
                if (!executor_list[editIndex].data) return;
                executor_list[editIndex].data = Object.assign(
                    executor_list[editIndex].data || {},
                    allValues,
                );

                updateNodeData(parentNode?.id, {
                    executor_list: executor_list,
                });
            } else {
                updateNodeData(node.id, allValues);
            }
        },
        [node?.id, updateNodeData, showChildNode],
    );

    const [searchParams] = useSearchParams();
    const publishStatus = searchParams.get('type') == 'true';
    // useNodeIdUpdate((nodeId, node) => {
    //     formRef?.current?.setFieldsValue({ desc: node?.data['desc'] || '' });
    //     formRef?.current?.setFieldsValue({ title: node?.data['title'] || '' });
    // });

    useEffect(() => {
        formRef?.current?.setFieldsValue({ desc: node?.data['desc'] || '' });
        formRef?.current?.setFieldsValue({ title: node?.data['title'] || '' });
    }, [node.id, showChildNode]);
    const runNode = () => {
        setTimeout(() => {
            setRunPanelNodeShow(node);
        }, 500);
    };

    const closeNodePanel = () => {
        if (node?.data?.['isChild']) {
            setSelect(node?.id, true);
            setShowChildNode(null);
        } else {
            setSelect(null);
        }
    };

    const RenderIcon = () => {
        if (node?.data?.baseData?.icon) {
            if (node?.type == BlockEnum.Tool) {
                return (
                    <div className="  size-8 rounded-md flex justify-center items-center" style={{backgroundColor:NODE_COLOR[node?.type]}}>
                        <img src={node?.data?.baseData?.icon} className="size-6" alt="" />
                    </div>
                );
            }
        }
        return (
            <div className=" bg-gray-300 size-8 rounded-md flex justify-center items-center"  style={{backgroundColor:NODE_COLOR[node?.type]}}>
                <img src={`/icons/${node?.type}.svg`} className="size-6" alt="" />
            </div>
        );
    };
    return (
        <ProForm
            className="mt-2"
            formRef={formRef}
            submitter={{ render: () => null }}
            onValuesChange={setNodeChange}
        >
            <div className="flex gap-2">
                <RenderIcon></RenderIcon>
                {/* focus: */}
                <ProFormText
                    formItemProps={{
                        className: 'flex-1',
                    }}
                    fieldProps={{
                        // variant: 'borderless',
                        className: 'font-bold text-base hover:bg-gray-100 border-none',
                    }}
                    allowClear={false}
                    name="title"
                    className="font-bold"
                ></ProFormText>
                {!publishStatus && !NOT_RUN_NODE_TYPE.includes(node?.type as BlockEnum) && (
                    <Tooltip
                        title={intl.formatMessage({
                            id: 'workflow.runThisNode',
                            defaultMessage: '',
                        })}
                    >
                        <Button
                            onClick={runNode}
                            icon={<CaretRightFilled></CaretRightFilled>}
                        ></Button>
                    </Tooltip>
                )}
                <Button onClick={closeNodePanel} icon={<CloseOutlined></CloseOutlined>}></Button>
            </div>

            <ProFormText
                formItemProps={{ className: 'mb-0' }}
                name="desc"
                allowClear={false}
                fieldProps={{
                    // variant: 'borderless',
                    className: '',
                }}
                placeholder={intl.formatMessage({
                    id: 'workflow.requireDes',
                    defaultMessage: '',
                })}
            ></ProFormText>
        </ProForm>
    );
});
export default memo(({ children, node }: { children: React.ReactNode; node: AppNode }) => {
    // let customNode = useReactive(node);
    const { updateNodeData } = useReactFlow();
    const addNode = useStore(state => state.addNode);
    const formRef = useRef(null);
    const runPanelShow = useStore(state => state.runPanelShow);
    const runPanelNodeShow = useStore(state => state.runPanelNodeShow);
    const ScrollContainerRef = useRef(null);
    const hasScrollBar = useScrollBarDetect(ScrollContainerRef);
    const [panelWidth, setPanelWidth] = useLocalStorageState('ani-workflow-panel-width', {
        defaultValue: 415,
    });

    useNodeIdUpdate((nodeId, node) => {
        // customNode = _.defaultsDeep(node, customNode);
    });

    const setNodeChange = (addItem: { [key: string]: any }, allValues) => {
        updateNodeData(node.id, allValues);
    };
    const handleResize = useCallback(
        (width: number) => {
            setPanelWidth(width);
        },
        [setPanelWidth],
    );
    const { triggerRef, containerRef } = useResizePanel({
        direction: 'horizontal',
        triggerDirection: 'left',
        minWidth: 415,
        maxWidth: 820,
        onResize: handleResize,
    });

    return (
        <div
            style={{
                right: runPanelShow ? '420px' : '',
            }}
            className="fixed dddddd duration-300 right-2 top-[105px] z-10 flex gap-2"
        >
            <div
                ref={containerRef}
                style={{ height: 'calc(100vh - 10px - 100px)', width: panelWidth + 'px' }}
                className="relative flex flex-col  p-4 w-96 shadow-lg rounded-md border border-blue-300 bg-white z-10 wrapPanel"
            >
                <div>
                    <div
                        ref={triggerRef}
                        className="absolute top-1/2 -translate-y-1/2 -left-2 w-3 h-6 cursor-col-resize resize-x"
                    >
                        <div className="w-1 h-6 bg-gray-300 rounded-sm"></div>
                    </div>
                    {/* <UserCon title={title} icon={node.type}></UserCon> */}

                    <NodeForm node={node} updateNodeData={updateNodeData} />
                    {/* <ProForm
                        className="mt-2"
                        formRef={formRef}
                        submitter={{
                            render: () => null,
                        }}
                        onValuesChange={setNodeChange}
                    >
                        <ProFormText
                            formItemProps={{
                                className: 'mb-0',
                            }}
                            name="desc"
                            placeholder={''}
                        ></ProFormText>
                    </ProForm> */}
                </div>

                <div
                    ref={ScrollContainerRef}
                    className={`overflow-y-auto flex-1 mt-4 ${hasScrollBar && 'pr-2'}`}
                >
                    {children}
                </div>

                <RunPanelNode></RunPanelNode>
            </div>
            {/* <div className='w-[400px] shadow-lg rounded-md border border-blue-300 bg-white'>
                <div>
                    <div className='text-base font-bold py-3 px-4'></div>
                    <Button icon={<DeleteOutlined></DeleteOutlined>}></Button>
                </div>


            </div> */}
        </div>
    );
});
