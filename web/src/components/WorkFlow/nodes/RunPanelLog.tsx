/*
 * @LastEditors: biz
 */
import { getWorkFlowLogInfo, updateDealtWith } from '@/api/workflow';
import FileDownloadList from '@/components/common/FileDownloadList';
import useUserStore from '@/store/user';
import useSocketStore from '@/store/websocket';
import {
    CheckCircleOutlined,
    CloseOutlined,
    LoadingOutlined,
    SyncOutlined,
} from '@ant-design/icons';
import { ProCard, ProForm, ProFormDateTimePicker, ProFormText } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useUpdateEffect } from 'ahooks';
import { Alert, Button, Collapse, Descriptions, Divider, Tag, Tooltip, Typography } from 'antd';
import _ from 'lodash';
import { memo, useCallback, useEffect, useRef, useState } from 'react';
import CodeEditor from '../components/Editor/CodeEditor';
import { NOT_SHOW_INPUT_RESULT_NODE, NOT_SHOW_OUTPUT_RESULT_NODE } from '../config';
import useSaveWorkFlow from '../saveWorkFlow';
import { BlockEnum } from '../types';

interface TodoTagProps {
    humanConfirmInfo: Array<{
        user_id: string | number;
        nickname: string;
    }>;
    userId: string | number;
    onClick?: (e: React.MouseEvent) => void;
}
export default memo(() => {
    const intl = useIntl();
    const runPanelLogRecord = useUserStore(state => state.runPanelLogRecord);
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const [runPanelShow, setRunPanelShow] = useState(false);
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    const setFlowMessage = useSocketStore(state => state.setFlowMessage);
    const flowMessage = useSocketStore(state => state.flowMessage);
    const [loading, setLoading] = useState(false);
    const [runList, setRunList] = useState([]);
    const [tabKey, setTabKey] = useState('4');
    const [endRun, setEndRun] = useState(null);
    const prevConfirmDealtWith = useUserStore(state => state.prevConfirmDealtWith);
    const saveWorkFlow = useSaveWorkFlow();
    const userId = JSON.parse(localStorage.getItem('userInfo') || '{}')?.uid;
    useUpdateEffect(() => {
        const newList = runList.map(item => {
            if (item.id == prevConfirmDealtWith.exec_id) {
                item.need_human_confirm = 0;
            }
            return item;
        });
        setRunList(newList);
    }, [prevConfirmDealtWith]);

    const TodoTag = memo(({ humanConfirmInfo, userId, onClick }: TodoTagProps) => {
        const intl = useIntl();

        const isSelfTodo = humanConfirmInfo?.some(x => x.user_id == userId);

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
    });
    const onClose = () => {
        setRunPanelLogRecord(null);
        setRunPanelShow(false);
        setTabKey('4');
        setEndRun(null);
        setRunList([]);
    };

    useUpdateEffect(() => {
        if (!runPanelLogRecord) {
            onClose();

            return;
        }
        setLoading(true);

        setRunPanelLogRecord(null);

        setTabKey('4');
        setEndRun(null);
        setRunList([]);

        getWorkFlowLogInfo(
            runPanelLogRecord.workflow_id,
            runPanelLogRecord.app_run_id || runPanelLogRecord.app_runs_id,
        ).then(res => {
            const list = res?.data?.list;
            if (res.code == 0) {
                setRunList(list);
                if (res?.data?.app_run_data) {
                    if (
                        res?.data?.app_run_data?.[0]?.status == 2 ||
                        res?.data?.app_run_data?.[0]?.status == 3
                    ) {
                        setEndRun({
                            ...res.data.app_run_data[0],
                            node_exec_data: list[list.length - 1],
                        });

                        console.log({
                            ...res.data.app_run_data[0],
                            node_exec_data: list[list.length - 1],
                        });

                        setTabKey('3');
                    }
                }
                setRunPanelShow(true);
            }
            setLoading(false);
        });
    }, [runPanelLogRecord]);

    const TrackContent = memo(props => {
        return (
            <div className="grid gap-2">
                {props?.runList?.map((item, index) => {
                    const nodeInfo = item;
                    const NodeChildren = useCallback(() => {
                        if (!nodeInfo) return null;

                        if (nodeInfo.status == 3 || (nodeInfo.status == 2 && item?.children)) {
                            return (
                                <div className="flex flex-col gap-2">
                                    {nodeInfo?.need_human_confirm ? (
                                        <div>
                                            <Alert
                                                message={
                                                    <div className="flex gap-2 flex-wrap ">
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
                                            ></Alert>
                                        </div>
                                    ) : null}
                                    {nodeInfo?.prompt_data?.length > 0 && (
                                        <div className="h-80">
                                            <CodeEditor
                                                language="python3"
                                                value={nodeInfo?.prompt_data}
                                                // mdValue={nodeInfo?.outputs_md}
                                                readOnly
                                                isJSONStringifyBeauty
                                                onChange={() => {}}
                                                title={intl.formatMessage({
                                                    id: 'workflow.historyPrompt',
                                                })}
                                            ></CodeEditor>
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
                                                ></CodeEditor>
                                            </div>
                                        )}
                                    {item?.child_executions && (
                                        <TrackContent
                                            runList={item?.child_executions}
                                        ></TrackContent>
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
                                                ></CodeEditor>
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
                        } else if (nodeInfo.status == 4) {
                            return (
                                <Alert
                                    message={
                                        item?.data?.error ||
                                        intl.formatMessage({ id: 'workflow.nodeRunError' })
                                    }
                                    type="error"
                                    className="text-red-700 break-all"
                                ></Alert>
                            );
                        }

                        return null;
                    }, [item]);

                    const delHumanMessage = id => {
                        const newFlowMessage = flowMessage.filter(
                            item =>
                                !(
                                    item?.data?.node_exec_data?.node_exec_id == id &&
                                    item?.type == 'workflow_need_human_confirm'
                                ),
                        );
                        setFlowMessage(newFlowMessage);
                    };

                    const NodeExtra = useCallback(() => {
                        if (item.human) {
                            if (nodeInfo?.status == 4) {
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
                                                await saveWorkFlow();
                                                updateDealtWith(
                                                    item.data.node_exec_data.node_exec_id,
                                                    {},
                                                ).then(async res => {
                                                    if (res.code == 0) {
                                                        delHumanMessage(
                                                            item.data.node_exec_data.node_exec_id,
                                                        );
                                                    }
                                                });
                                            }}
                                        >
                                            {intl.formatMessage({ id: 'workflow.resetRun' })}
                                        </Tag>
                                    </Tooltip>
                                );
                            }
                            return (
                                <Tooltip
                                    title={intl.formatMessage({ id: 'workflow.clickToBackLogs' })}
                                >
                                    <Tag
                                        icon={<SyncOutlined spin />}
                                        color="processing"
                                        className="mr-0"
                                        onClick={e => {
                                            e.stopPropagation();
                                            setDealtWithData(item);
                                        }}
                                    >
                                        {intl.formatMessage({ id: 'workflow.backlogs' })}
                                    </Tag>
                                </Tooltip>
                            );
                        }

                        if (nodeInfo.node_type == BlockEnum.Human) {
                            if (nodeInfo.need_human_confirm == 1) {
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
                                    icon={<CheckCircleOutlined></CheckCircleOutlined>}
                                    color="success"
                                    className="mr-0"
                                >
                                    {intl.formatMessage({ id: 'workflow.checkedBackLogs' })}
                                </Tag>
                            );
                        }

                        if (nodeInfo.status == 2) {
                            return <LoadingOutlined />;
                        } else if (nodeInfo?.status == 3) {
                            return (
                                <div>
                                    <div className="flex items-center gap-1">
                                        <span>
                                            {_.clamp(item?.elapsed_time, 0.00001, 9999999).toFixed(
                                                5,
                                            )}
                                            S
                                        </span>
                                        <CheckCircleOutlined className="text-green-400"></CheckCircleOutlined>
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
                    }, [item, userId]);
                    return (
                        <div className="user-collapse">
                            <Collapse
                                key={index}
                                items={[
                                    {
                                        key: '1',
                                        // extra: <>9.1131ms·0 tokens</>,
                                        label: (
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <div className=" bg-gray-300 size-7 rounded-md flex justify-center items-center">
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
                                                    <NodeExtra></NodeExtra>
                                                </div>
                                            </div>
                                        ),
                                        children: <NodeChildren></NodeChildren>,
                                    },
                                ]}
                            />
                        </div>
                    );
                })}
            </div>
        );
    });

    return runPanelShow ? (
        <ProCard
            className="w-[400px] border user_pro_card_overflow_y border-blue-300 fixed z-20  top-[65px] right-2 "
            style={{ height: 'calc(100vh - 10px - 75px)' }}
            extra={
                <Button
                    type="text"
                    onClick={onClose}
                    icon={<CloseOutlined></CloseOutlined>}
                ></Button>
            }
            title={
                <Typography.Title level={5}>
                    {intl.formatMessage({ id: 'workflow.runLogs' })}
                </Typography.Title>
            }
            bodyStyle={{
                overflowY: 'auto',
            }}
            loading={loading}
            tabs={{
                tabPosition: 'top',
                activeKey: tabKey,

                items: [
                    {
                        label: intl.formatMessage({ id: 'workflow.result' }),
                        key: '3',
                        disabled: !endRun,
                        children: <DetailContent endRun={endRun}></DetailContent>,
                    },
                    {
                        label: intl.formatMessage({ id: 'workflow.backTo' }),
                        key: '4',

                        children: (
                            <div className="">
                                <TrackContent runList={runList}></TrackContent>
                            </div>
                        ),
                    },
                ],
                onChange: setTabKey,
            }}
        ></ProCard>
    ) : null;
});
const DetailContent = memo(({ endRun }: { endRun: any }) => {
    const intl = useIntl();
    const [messageType, setMessageType] = useState<'success' | 'fail'>('fail');
    const form = useRef(null);
    const [code, setCode] = useState('');
    const messConfig = {
        statusClass: {
            success: 'green-700',
            fail: 'red-700',
        },
        message: {
            success: 'Success',
            fail: 'Fail',
        },
        messageType: {
            success: 'success',
            fail: 'error',
        },
    } as const;
    type MessConfigKeys = keyof typeof messConfig;
    const getMessage = useCallback(
        (configName: MessConfigKeys) => {
            return messConfig[configName][messageType];
        },
        [messageType],
    );

    // useEffect(() => {
    //     if (endRun) {
    //         console.log(endRun);

    //         // form?.current.setFieldsValue({
    //         //     status: endRun?.status == 3 ? 'fail' : 'success',
    //         //     elapsed_time: endRun?.elapsed_time?.toFixed(4) || 0,
    //         //     completion_tokens: endRun?.completion_tokens || '',
    //         //     created_time: endRun?.created_time || '',
    //         //     total_tokens: endRun?.total_tokens || '',
    //         //     actual_completed_steps: endRun?.actual_completed_steps || '',
    //         // });
    //         setMessageType(endRun?.status == 3 ? 'fail' : 'success');
    //     }
    // }, [endRun]);
    const Message = () => {
        return (
            <div>
                <div className="grid grid-cols-3">
                    <div>
                        <div className="text-gray-500 text-sm">
                            {intl.formatMessage({ id: 'workflow.status' })}
                        </div>
                        <div
                            className={`text-${getMessage(
                                'statusClass',
                            )} font-bold text-base flex gap-2 items-center`}
                        >
                            <div className={`size-2  bg-${getMessage('statusClass')}`}></div>
                            {getMessage('message')}
                        </div>
                    </div>
                    <div>
                        <div className="text-gray-500 text-sm">
                            {intl.formatMessage({ id: 'workflow.elapsed_time' })}
                        </div>
                        <div className="font-bold text-base">
                            {endRun?.elapsed_time?.toFixed(4) || 0}s
                        </div>
                    </div>
                    <div>
                        <div className="text-gray-500 text-sm">
                            {intl.formatMessage({ id: 'workflow.completion_tokens' })}
                        </div>
                        <div className=" font-bold text-base">
                            {endRun?.total_tokens || 0} Tokens
                        </div>
                    </div>
                </div>
            </div>
        );
    };
    const getStatusTag = (status: number) => {
        const statusMap = {
            1: { color: 'processing', text: intl.formatMessage({ id: 'workflow.running' }) },
            2: { color: 'success', text: intl.formatMessage({ id: 'workflow.runSc' }) },
            3: { color: 'error', text: intl.formatMessage({ id: 'workflow.runF' }) },
        };
        const currentStatus = statusMap[status] || { color: 'default', text: 'Unknown' };
        return <Tag color={currentStatus.color}>{currentStatus.text}</Tag>;
    };
    const alertType = getMessage('messageType') as 'success' | 'error';
    return (
        <>
            {/* <Badge.Ribbon text='Fail' color='red'> */}
            {/* <Alert message={<Message></Message>} className="break-all" type={alertType}></Alert> */}

            <Descriptions column={1} bordered size="small">
                <Descriptions.Item label={intl.formatMessage({ id: 'workflow.status' })}>
                    {/* {getMessage('message')} */}
                    {getStatusTag(endRun?.status)}
                </Descriptions.Item>
                <Descriptions.Item label={intl.formatMessage({ id: 'workflow.created_time' })}>
                    {endRun?.created_time}
                </Descriptions.Item>
                <Descriptions.Item label={intl.formatMessage({ id: 'workflow.elapsed_time' })}>
                    {endRun?.elapsed_time?.toFixed(4) || 0}s
                </Descriptions.Item>
                <Descriptions.Item label={intl.formatMessage({ id: 'workflow.completion_tokens' })}>
                    {endRun?.total_tokens || 0} Tokens
                </Descriptions.Item>

                <Descriptions.Item
                    label={intl.formatMessage({ id: 'workflow.actual_completed_steps' })}
                >
                    {endRun?.actual_completed_steps}
                </Descriptions.Item>
            </Descriptions>
            {endRun?.node_exec_data?.outputs && (
                <div className="h-80 mt-4">
                    <CodeEditor
                        language="python3"
                        value={endRun?.node_exec_data?.outputs}
                        mdValue={endRun?.node_exec_data?.outputs_md}
                        readOnly
                        isJSONStringifyBeauty
                        // onChange={handleCodeChange}
                        title={intl.formatMessage({ id: 'workflow.outputs' })}
                    ></CodeEditor>
                </div>
            )}
            {endRun?.node_exec_data?.file_list?.length > 0 && (
                <FileDownloadList
                    files={endRun.node_exec_data.file_list}
                    title={intl.formatMessage({ id: 'skill.downloadFiles' })}
                    className="mt-4"
                />
            )}
            {/* <div className='text-sm font-bold mt-4 mb-2'>

            </div> */}
            {/* <Divider orientationMargin="0" orientation="left">
                {intl.formatMessage({ id: 'workflow.orcompute' })}
            </Divider> */}

            {/* <ProForm
                layout="horizontal"
                formRef={form}
                submitter={false}
                labelAlign="left"
                labelCol={{ span: 8 }}
                wrapperCol={{ span: 16 }}
            >
                <ProFormText
                    formItemProps={{
                        className: '!mb-0',
                    }}
                    readonly
                    label={intl.formatMessage({ id: 'workflow.status' })}
                    name="status"
                ></ProFormText>
          
                <ProFormDateTimePicker
                    formItemProps={{
                        className: '!mb-0',
                    }}
                    readonly
                    label={intl.formatMessage({ id: 'workflow.created_time' })}
                    name="created_time"
                ></ProFormDateTimePicker>
                <ProFormText
                    formItemProps={{
                        className: '!mb-0',
                    }}
                    readonly
                    label={intl.formatMessage({ id: 'workflow.elapsed_time' })}
                    name="elapsed_time"
                ></ProFormText>
                <ProFormText
                    formItemProps={{
                        className: '!mb-0',
                    }}
                    readonly
                    label={intl.formatMessage({ id: 'workflow.completion_tokens' })}
                    name="total_tokens"
                ></ProFormText>
                <ProFormText
                    formItemProps={{
                        className: '!mb-0',
                    }}
                    readonly
                    label={intl.formatMessage({ id: 'workflow.actual_completed_steps' })}
                    name="actual_completed_steps"
                ></ProFormText>
            </ProForm> */}
            {/* </Badge.Ribbon> */}
        </>
    );
});
