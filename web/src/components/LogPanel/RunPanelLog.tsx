/*
 * @LastEditors: biz
 */
import { getWorkFlowLogInfo, pauseResumeWorkflow } from '@/api/workflow';
import FileDownloadList from '@/components/common/FileDownloadList';
import useUserStore from '@/store/user';
import useSocketStore from '@/store/websocket';
import { CloseOutlined, PauseOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { ProCard } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useLatest, useUpdateEffect } from 'ahooks';
import { Button, Descriptions, Skeleton, Tag, Typography, Tooltip, message } from 'antd';
import { memo, useCallback, useState } from 'react';
import CodeEditor from '../WorkFlow/components/Editor/CodeEditor';
import { TrackContent } from './components/TrackContent';

interface TodoTagProps {
    humanConfirmInfo: Array<{
        user_id: string | number;
        nickname: string;
    }>;
    userId: string | number;
    onClick?: (e: React.MouseEvent) => void;
}

const DetailContent = memo(({ endRun }: { endRun: any }) => {
    const intl = useIntl();

    const getStatusTag = (status: number) => {
        const statusMap = {
            1: { color: 'processing', text: intl.formatMessage({ id: 'workflow.running' }) },
            2: { color: 'success', text: intl.formatMessage({ id: 'workflow.runSc' }) },
            3: { color: 'error', text: intl.formatMessage({ id: 'workflow.runF' }) },
        };
        const currentStatus = statusMap[status] || { color: 'default', text: 'Unknown' };
        return <Tag color={currentStatus.color}>{currentStatus.text}</Tag>;
    };

    return (
        <>
            <Descriptions column={1} bordered size="small">
                <Descriptions.Item label={intl.formatMessage({ id: 'workflow.status' })}>
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
        </>
    );
});

export default memo(() => {
    const intl = useIntl();
    const runPanelLogRecord = useUserStore(state => state.runPanelLogRecord);
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const [runPanelShow, setRunPanelShow] = useState(false);

    const [loading, setLoading] = useState(false);
    const [runList, setRunList] = useState([]);
    const [tabKey, setTabKey] = useState('4');
    const [endRun, setEndRun] = useState(null);
    const [detail, setDetail] = useState(null);
    const prevConfirmDealtWith = useUserStore(state => state.prevConfirmDealtWith);

    const [appRunId, setAppRunId] = useState(null);
    const lastAppRunId = useLatest(appRunId);

    const getLastRunWorkflow = useSocketStore(state => state.lastMessage);

    const [updateCounter, setUpdateCounter] = useState(0);
    const [isPaused, setIsPaused] = useState(false);
    const [showPauseResume, setShowPauseResume] = useState(false);

    useUpdateEffect(() => {
        const newList = runList.map(item => {
            if (item.id == prevConfirmDealtWith.exec_id) {
                return { ...item, need_human_confirm: 0 };
            }
            return item;
        });
        setRunList(newList);
    }, [prevConfirmDealtWith]);

    useUpdateEffect(() => {
        if (
            getLastRunWorkflow?.type != 'workflow_run_debug' ||
            getLastRunWorkflow?.data?.app_run_id != lastAppRunId.current?.app_run_id
        ) {
            return console.log('pass');
        }
        setLoading(true);

        getDetail(lastAppRunId.current)
            .then(() => {
                setUpdateCounter(prev => prev + 1);
                setLoading(false);
            })
            .catch(err => {
                console.error('Error fetching details:', err);
                setLoading(false);
            });
    }, [getLastRunWorkflow]);

    const onClose = useCallback(() => {
        setRunPanelLogRecord(null);
        setRunPanelShow(false);
        setTabKey('4');
        setEndRun(null);
        setRunList([]);
    }, [setRunPanelLogRecord]);

    useUpdateEffect(() => {
        if (!runPanelLogRecord) {
            return;
        }

        setLoading(true);
        setRunPanelLogRecord(null);
        setTabKey('4');
        setEndRun(null);
        setRunList([]);
        setAppRunId(runPanelLogRecord);
        setRunPanelShow(true);

        getDetail(runPanelLogRecord)
            .then(() => {
                setRunPanelShow(true);
                setUpdateCounter(prev => prev + 1);
                setLoading(false);
            })
            .catch(err => {
                console.error('Error fetching details:', err);
                setLoading(false);
            });
    }, [runPanelLogRecord, onClose]);

    const getDetail = useCallback(
        async runPanelLogRecord => {
            if (!runPanelLogRecord?.workflow_id) return { code: -1 };

            try {
                const res = await getWorkFlowLogInfo(
                    runPanelLogRecord.workflow_id,
                    runPanelLogRecord.app_run_id || runPanelLogRecord.app_runs_id,
                );

                if (res.code === 0) {
                    const list = res?.data?.list || [];

                    setRunList(list);
                    setDetail(res?.data?.app_run_data?.[0]);
                    const appRunData = res?.data?.app_run_data?.[0];
                    
                    // Handle pause/resume button visibility and state
                    // Only show pause/resume button if status is 1 (running)
                    if (appRunData?.status === 1) {
                        setShowPauseResume(true);
                        setIsPaused(appRunData?.paused === 1);
                    } else {
                        setShowPauseResume(false);
                    }
                    
                    if (appRunData?.status === 2 || appRunData?.status === 3) {
                        setEndRun({
                            ...appRunData,
                            node_exec_data: list[list.length - 1],
                        });
                        setTabKey('3');
                    }
                }

                return res;
            } catch (error) {
                console.error('Failed to fetch workflow log info:', error);
                return { code: -1 };
            }
        },
        [appRunId, runPanelLogRecord],
    );

    // Handle pause/resume workflow
    const handlePauseResume = useCallback(async () => {
        if (!detail?.app_run_id) {
            message.error(intl.formatMessage({ id: 'workflow.noAppRunId', defaultMessage: 'No app run ID found' }));
            return;
        }

        try {
            const pausedValue = isPaused ? 0 : 1; // 0 for resume, 1 for pause
            const res = await pauseResumeWorkflow(Number(detail.app_run_id), pausedValue);
            
            if (res?.code === 0) {
                setIsPaused(!isPaused);
                // Display message from API response
                if (res?.data?.msg) {
                    message.success(res.data.msg);
                }
                
                // Refresh the detail to get updated status
                if (appRunId) {
                    getDetail(appRunId);
                }
            } else {
                message.error(res?.message);
            }
        } catch (err) {
            console.error('Error pausing/resuming workflow:', err);
            // Only console.error for exceptions, no message.error
        }
    }, [detail, isPaused, intl, appRunId, getDetail]);

    const TrackContentWrapper = memo(() => {
        if (loading) {
            return (
                <div className="w-full space-y-4 p-4">
                    <Skeleton active paragraph={{ rows: 3 }} />
                </div>
            );
        }
        return (
            <TrackContent
                detail={detail}
                runList={runList}
                onClose={onClose}
                updateKey={updateCounter}
            />
        );
    });

    if (!runPanelShow) {
        return null;
    }

    return (
        <ProCard
            className="w-[400px] border user_pro_card_overflow_y border-blue-300 fixed z-20 top-[65px] right-2"
            style={{ height: 'calc(100vh - 10px - 75px)' }}
            extra={
                <div className="flex items-center gap-3">
                    {showPauseResume && (
                        <Tooltip 
                            title={isPaused 
                                ? intl.formatMessage({ id: 'workflow.resumeRun', defaultMessage: 'Resume Run' })
                                : intl.formatMessage({ id: 'workflow.pauseRun', defaultMessage: 'Pause Run' })
                            }
                        >
                            <Button
                                type="primary"
                                size="small"
                                onClick={handlePauseResume}
                                icon={isPaused ? <PlayCircleOutlined /> : <PauseOutlined />}
                                className="bg-blue-500 hover:bg-blue-600 border-blue-500 hover:border-blue-600"
                            >
                            </Button>
                        </Tooltip>
                    )}
                    <Button type="text" onClick={onClose} icon={<CloseOutlined />} />
                </div>
            }
            title={
                <Typography.Title level={5}>
                    {intl.formatMessage({ id: 'workflow.runLogs' })}
                    {detail?.type === 1 && ` (${intl.formatMessage({ id: 'workflow.debugRun' })})`}
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
                        children: <DetailContent endRun={endRun} />,
                    },
                    {
                        label: intl.formatMessage({ id: 'workflow.backTo' }),
                        key: '4',
                        children: <TrackContentWrapper />,
                    },
                ],
                onChange: setTabKey,
            }}
        />
    );
});
