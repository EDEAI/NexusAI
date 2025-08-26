import { updateDealtWith } from '@/api/workflow';
import FileDownloadList from '@/components/common/FileDownloadList';
import useUserStore from '@/store/user';
import useSocketStore from '@/store/websocket';
import { CheckCircleOutlined, LoadingOutlined, SyncOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { useLatest } from 'ahooks';
import { Alert, Collapse, message, Tag, Tooltip } from 'antd';
import _ from 'lodash';
import { memo, useEffect } from 'react';
import CodeEditor from '../../WorkFlow/components/Editor/CodeEditor';
import { NOT_SHOW_INPUT_RESULT_NODE, NOT_SHOW_OUTPUT_RESULT_NODE } from '../../WorkFlow/config';
import useSaveWorkFlow from '../../WorkFlow/saveWorkFlow';
import { BlockEnum } from '../../WorkFlow/types';
import { useUserInfo } from '@/hooks/useUserInfo';

interface TrackContentProps {
    runList: any[];
    updateKey?: number;
    onClose?: () => void;
    detail?: any;
}

export const TrackContent = memo(
    ({ runList = [], updateKey, onClose, detail }: TrackContentProps) => {
        const intl = useIntl();
        const setDealtWithData = useUserStore(state => state.setDealtWithData);
        const setFlowMessage = useSocketStore(state => state.setFlowMessage);
        const flowMessage = useSocketStore(state => state.flowMessage);
        const saveWorkFlow = useSaveWorkFlow();
        const { userInfo } = useUserInfo();
        const userId = userInfo?.uid;
        const lastDetail = useLatest(detail);

        useEffect(() => {
            console.log('TrackContent received runList:', runList.length, 'updateKey:', updateKey);
        }, [runList, updateKey]);

        const delHumanMessage = id => {
            const newFlowMessage = flowMessage.filter(
                item =>
                    !(
                        item?.data?.node_exec_data?.node_exec_id === id &&
                        item?.type === 'workflow_need_human_confirm'
                    ),
            );
            setFlowMessage(newFlowMessage);
        };

        // TodoTag 内联定义
        const TodoTag = ({ humanConfirmInfo, userId, onClick }) => {
            const isSelfTodo = humanConfirmInfo?.some(x => x.user_id === parseInt(userId));
            console.log(runList, detail);
    
            if (lastDetail?.current?.type == 1) {
                return (
                    <Tooltip
                        title={intl.formatMessage({
                            id: 'workflow.debugRunWait',
                        })}
                    >
                        <Tag className="flex items-center justify-center" color="blue">
                            {intl.formatMessage({ id: 'workflow.debugTodo' })}
                        </Tag>
                    </Tooltip>
                );
            }
            return (
                <Tooltip
                    title={intl.formatMessage(
                        { id: 'workflow.tooltip.confirmer' },
                        {
                            users: humanConfirmInfo?.map(x => x.nickname).join(','),
                        },
                    )}
                >
                    <Tag
                        className="flex items-center justify-center"
                        color="blue"
                        onClick={isSelfTodo ? onClick : undefined}
                    >
                        {intl.formatMessage({
                            id: isSelfTodo
                                ? 'workflow.needHumanConfirm1'
                                : 'workflow.needHumanConfirm2',
                        })}
                    </Tag>
                </Tooltip>
            );
        };

        return (
            <div className="grid gap-2">
                {runList.map((item, index) => {
                    const nodeInfo = item;

                    // NodeChildren 组件内联定义
                    const NodeChildren = () => {
                        if (!nodeInfo) return null;

                        if (item?.child_executions?.length) {
                            return (
                                <TrackContent
                                    detail={lastDetail?.current}
                                    runList={item?.child_executions}
                                />
                            );
                        }

                        if (nodeInfo.status === 3 || (nodeInfo.status === 2 && item?.children)) {
                            return (
                                <div className="flex flex-col gap-2">
                                    {nodeInfo?.need_human_confirm?.length > 0 ? (
                                        <div>
                                            <Alert
                                                message={
                                                    <div className="flex gap-2 flex-wrap">
                                                        {intl.formatMessage({
                                                            id: 'workflow.label.confirmer',
                                                        })}{' '}
                                                        :
                                                        {item?.human_confirm_info
                                                            ?.map(item => item.nickname)
                                                            .join('、')}
                                                    </div>
                                                }
                                                type="info"
                                                className="break-all"
                                            />
                                        </div>
                                    ) : null}

                                    {nodeInfo?.prompt_data?.length > 0 && (
                                        <div className="h-80">
                                            <CodeEditor
                                                language="python3"
                                                value={nodeInfo?.prompt_data}
                                                readOnly
                                                isJSONStringifyBeauty
                                                onChange={() => {}}
                                                title={intl.formatMessage({
                                                    id: 'workflow.historyPrompt',
                                                })}
                                            />
                                        </div>
                                    )}

                                    {nodeInfo.inputs &&
                                        !NOT_SHOW_INPUT_RESULT_NODE.includes(
                                            nodeInfo.node_type,
                                        ) && (
                                            <div className="h-80">
                                                <CodeEditor
                                                    language="python3"
                                                    value={nodeInfo?.inputs}
                                                    readOnly
                                                    isJSONStringifyBeauty
                                                    onChange={() => {}}
                                                    title={intl.formatMessage({
                                                        id: 'workflow.inputs',
                                                    })}
                                                />
                                            </div>
                                        )}

                                    {item?.child_executions && (
                                        <TrackContent
                                            detail={lastDetail?.current}
                                            runList={item?.child_executions}
                                        />
                                    )}

                                    {nodeInfo.outputs &&
                                        !NOT_SHOW_OUTPUT_RESULT_NODE.includes(
                                            nodeInfo.node_type,
                                        ) && (
                                            <div className="h-80 w-[320px]">
                                                <CodeEditor
                                                    language="python3"
                                                    value={nodeInfo?.outputs}
                                                    mdValue={nodeInfo?.outputs_md}
                                                    readOnly
                                                    isJSONStringifyBeauty
                                                    onChange={() => {}}
                                                    title={intl.formatMessage({
                                                        id: 'workflow.outputs',
                                                    })}
                                                />
                                            </div>
                                        )}

                                    {nodeInfo.file_list && nodeInfo.file_list.length > 0 && (
                                        <FileDownloadList
                                            files={nodeInfo.file_list}
                                            title={intl.formatMessage({
                                                id: 'skill.downloadFiles',
                                            })}
                                            className="w-[314px]"
                                        />
                                    )}
                                </div>
                            );
                        } else if (nodeInfo.status === 4) {
                            return (
                                <Alert
                                    message={
                                        item?.error ||
                                        intl.formatMessage({ id: 'workflow.nodeRunError' })
                                    }
                                    type="error"
                                    className="text-red-700 break-all"
                                />
                            );
                        }

                        return null;
                    };

                    // NodeExtra 组件内联定义
                    const NodeExtra = () => {
                        if (nodeInfo?.status === 4) {
                            return (
                                <Tooltip
                                    title={intl.formatMessage({
                                        id: 'workflow.nodeRunErrorDes',
                                    })}
                                >
                                    <Tag
                                        icon={<SyncOutlined spin />}
                                        color="error"
                                        className="mr-0"
                                        onClick={async e => {
                                            e.stopPropagation();
                                            console.log(item);

                                            const res = await updateDealtWith(item.id, {});
                                            if (res.code === 0) {
                                                message.success(
                                                    intl.formatMessage({
                                                        id: 'workflow.resetRunSuccess',
                                                    }),
                                                );
                                                // delHumanMessage(item.data.node_exec_data.node_exec_id);
                                                onClose?.();
                                            }
                                        }}
                                    >
                                        {intl.formatMessage({ id: 'workflow.resetRun' })}
                                    </Tag>
                                </Tooltip>
                            );
                        }

                        if (nodeInfo.node_type === BlockEnum.Human) {
                            if (nodeInfo.need_human_confirm === 1) {
                                return (
                                    <TodoTag
                                        humanConfirmInfo={item.human_confirm_info}
                                        userId={userId}
                                        onClick={e => {
                                            e.stopPropagation();
                                            setDealtWithData({
                                                ...item,
                                                exec_id: item.id,
                                            });
                                        }}
                                    />
                                );
                            }
                            return (
                                <Tag
                                    icon={<CheckCircleOutlined />}
                                    color="success"
                                    className="mr-0"
                                >
                                    {intl.formatMessage({ id: 'workflow.checkedBackLogs' })}
                                </Tag>
                            );
                        }

                        if (nodeInfo.status === 2) {
                            return <LoadingOutlined />;
                        } else if (nodeInfo?.status === 3) {
                            return (
                                <div>
                                    <div className="flex items-center gap-1">
                                        <span>
                                            {_.clamp(item?.elapsed_time, 0.00001, 9999999).toFixed(
                                                5,
                                            )}
                                            S
                                        </span>
                                        <CheckCircleOutlined className="text-green-400" />
                                    </div>
                                    {item?.need_human_confirm ? (
                                        <TodoTag
                                            humanConfirmInfo={item.human_confirm_info}
                                            userId={userId}
                                            onClick={e => {
                                                e.stopPropagation();
                                                setDealtWithData({
                                                    ...item,
                                                    exec_id: item.id,
                                                });
                                            }}
                                        />
                                    ) : null}
                                </div>
                            );
                        }

                        return <span className="text-red-500">ERROR</span>;
                    };

                    return (
                        <div className="user-collapse" key={`${item.id || index}-${updateKey}`}>
                            <Collapse
                                defaultActiveKey={
                                    item?.child_executions?.length && nodeInfo.status == 2
                                        ? '1'
                                        : '2'
                                }
                                items={[
                                    {
                                        key: '1',
                                        label: (
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <div className="bg-gray-300 size-7 rounded-md flex justify-center items-center">
                                                        <img
                                                            src={`/icons/${item.node_graph.data.type}.svg`}
                                                            className="size-6"
                                                            alt=""
                                                        />
                                                    </div>
                                                    <div className="flex-1 shrink-0">
                                                        {item.node_graph.data.title}
                                                        <div className="text-[10px] text-slate-500">
                                                            {item.finished_time}
                                                        </div>
                                                    </div>
                                                    <NodeExtra />
                                                </div>
                                            </div>
                                        ),
                                        children: <NodeChildren />,
                                    },
                                ]}
                            />
                        </div>
                    );
                })}
            </div>
        );
    },
);
