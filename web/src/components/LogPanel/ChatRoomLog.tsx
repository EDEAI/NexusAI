/*
 * @LastEditors: biz
 */
import { getMeetingSummaryHistorySingle } from '@/api/plaza';
import ResizablePanel from '@/components/Panel/DraggablePanel';
import { CloseOutlined } from '@ant-design/icons';
import { ProCard } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useRequest } from 'ahooks';
import { Button, Descriptions, Spin, Tag, Timeline, Typography } from 'antd';
import { memo, useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import Graphic from '../Graphic';
import { getProperties, ProgressContainer } from '@/pages/Plaza/components/MeetingSummary/components/SummaryHistoryDom';
import useUserStore from '@/store/user';

export default memo(
    ({
        data,
        onClose,
    }: {
        data: { chatroom_id: string; app_run_id: string };
        onClose?: () => void;
    }) => {
        const intl = useIntl();
        const [panelWidth, setPanelWidth] = useState(500);
        const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
        const {
            data: logDetail,
            loading,
            run,
        } = useRequest(
            async (chatroom_id, app_run_id) => {
                const res = await getMeetingSummaryHistorySingle({
                    chatroom_id,
                    app_run_id,
                });
                return res.data;
            },
            {
                manual: true,
            },
        );

        useEffect(() => {
            if (data?.chatroom_id && data?.app_run_id) {
                run(data.chatroom_id, data.app_run_id);
            }
        }, [data?.chatroom_id, data?.app_run_id, run]);

        const getStatusTag = (status: number) => {
            const statusMap = {
                1: { color: 'processing', text: intl.formatMessage({ id: 'workflow.running' }) },
                2: { color: 'success', text: intl.formatMessage({ id: 'workflow.runSc' }) },
                3: { color: 'error', text: intl.formatMessage({ id: 'workflow.runF' }) },
            };
            const currentStatus = statusMap[status] || { color: 'default', text: 'Unknown' };
            return <Tag color={currentStatus.color}>{currentStatus.text}</Tag>;
        };

        const handleResize = (width: number) => {
            setPanelWidth(width);
        };

        return (
            <ResizablePanel
                className="fixed top-[65px] right-2 p-0"
                dragDirection="left"
                minWidth={400}
                maxWidth={800}
                defaultWidth={panelWidth}
                onChange={handleResize}
            >
                <ProCard
                    className="border-none h-full"
                    style={{
                        height: 'calc(100vh - 50px - 60px)',
                    }}
                    bodyStyle={{ overflowY: 'auto', padding: '16px' }}
                    extra={
                        <Button
                            type="text"
                            className="-mr-4 -mt-8"
                            onClick={onClose}
                            icon={<CloseOutlined />}
                        />
                    }
                    title={
                        <Typography.Title level={5}>
                            {intl.formatMessage({ id: 'app.chatroom.log.title' })}
                        </Typography.Title>
                    }
                    loading={loading}
                >
                    <div className="space-y-6">
                        {loading ? (
                            <div className="flex items-center justify-center h-40">
                                <Spin />
                            </div>
                        ) : logDetail?.source_run ? (
                            <>
                                <Descriptions column={1} bordered size="small">
                                    <Descriptions.Item
                                        label={intl.formatMessage({ id: 'app.chatroom.log.name' })}
                                    >
                                        {logDetail.source_run.name}
                                    </Descriptions.Item>
                                    {/* <Descriptions.Item
                                        label={intl.formatMessage({ id: 'workflow.status' })}
                                    >
                                        {getStatusTag(logDetail.source_run.status)}
                                    </Descriptions.Item> */}
                                    <Descriptions.Item
                                        label={intl.formatMessage({ id: 'workflow.created_time' })}
                                    >
                                        {logDetail.source_run.created_time}
                                    </Descriptions.Item>
                                    <Descriptions.Item
                                        label={intl.formatMessage({ id: 'workflow.finished_time' })}
                                    >
                                        {logDetail.source_run.finished_time}
                                    </Descriptions.Item>
                                    <Descriptions.Item
                                        label={intl.formatMessage({ id: 'workflow.elapsed_time' })}
                                    >
                                        {logDetail.source_run.elapsed_time}s
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Tokens">
                                        {logDetail.source_run.total_tokens}
                                    </Descriptions.Item>
                                </Descriptions>

                                <div className="mt-4">
                                    <Typography.Title level={5}>讨论总结</Typography.Title>
                                    <p className="text-[12px] color-[#eee] mb-[8px]">
                                        {logDetail.source_run.created_time}
                                    </p>
                                    <div>
                                        <div
                                            className={`p-[12px]  leading-[22px] bg-gray-50 rounded mt-2`}
                                        >
                                            <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                                                {logDetail?.source_run?.summary}
                                            </ReactMarkdown>
                                        </div>
                                    </div>
                                </div>

                              

                                {logDetail?.source_corrections &&
                                logDetail?.source_corrections.length > 0 ? (
                                    <div>
                                        <div className="text-[16px] font-[600] py-[8px]">
                                            {intl.formatMessage({
                                                id: 'app.summaryhistory.orientation',
                                            })}
                                            :
                                        </div>
                                        {logDetail?.source_corrections.map((citem, index) => (
                                            <div
                                                key={citem.created_time}
                                                className="mb-[16px] last-of-type:mb-0"
                                            >
                                                <div
                                                    className={`rounded-[4px]  ${
                                                        logDetail?.source_corrections.length - 1 !=
                                                        index
                                                            ? 'bg-[#F7F7F7]'
                                                            : 'bg-blue-100'
                                                    }`}
                                                >
                                                    <div className="p-[12px]   leading-[22px]">
                                                        <div className="tetx-[14px] font-[600] pb-[12px]">
                                                            {intl.formatMessage({
                                                                id: 'app.summaryhistory.userPrompt',
                                                            })}
                                                            : {citem.user_prompt}
                                                        </div>
                                                        <div className="tetx-[14px] font-[600] pb-[12px]">
                                                            {intl.formatMessage({
                                                                id: 'app.summaryhistory.time',
                                                            })}
                                                            : {citem.created_time}
                                                        </div>
                                                        <ReactMarkdown
                                                            rehypePlugins={[rehypeHighlight]}
                                                        >
                                                            {citem?.corrected_summary}
                                                        </ReactMarkdown>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <></>
                                )}

                                {logDetail?.target_run ? (
                                    <div className="py-[12px]">
                                        <div className="text-[16px] font-[600] py-[8px]">
                                            {intl.formatMessage({
                                                id: 'app.summaryhistory.runapp',
                                            })}
                                            :
                                        </div>
                                        <div>
                                            <div className="text-[14px] py-[6px]">
                                                <span className="font-[500] ">
                                                    {logDetail?.target_run?.agent_id
                                                        ? 'agent'
                                                        : 'workflow'}
                                                </span>
                                                <span className="px-[6px]">:</span>
                                                <span>{logDetail?.target_run?.app?.name}</span>
                                            </div>
                                        </div>
                                        <div>
                                            {logDetail?.target_run?.inputs?.properties ? (
                                                <div>
                                                    <div className="text-[16px] color-[#000] font-[600] py-[12px]">
                                                        {intl.formatMessage({
                                                            id: 'app.summaryhistory.input',
                                                        })}
                                                        :
                                                    </div>
                                                    {getProperties(
                                                        logDetail?.target_run?.inputs?.properties,
                                                    ).map(i => (
                                                        <div className="pb-[10px]">
                                                            <div className="pb-[8px] font-[600]">
                                                                {i.display_name || i.name}
                                                            </div>
                                                            {/* <Input.TextArea variant='borderless' className='text-[14px]' value={item.value}  rows={6}/> */}
                                                            <div className="py-[4px] px-[11px] text-[14px] leading-[1.5] h-[]">
                                                                {i.value}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <></>
                                            )}
                                        </div>
                                        <div>
                                            {logDetail?.target_run?.raw_user_prompt ? (
                                                <div>
                                                    <div className="text-[16px] color-[#000] font-[600] py-[12px] pb-[6px]">
                                                        {intl.formatMessage({
                                                            id: 'app.summaryhistory.prompt',
                                                        })}
                                                        :
                                                    </div>
                                                    <div className="py-[4px] px-[11px] text-[14px] leading-[1.5] ">
                                                        {logDetail?.target_run?.raw_user_prompt}
                                                    </div>
                                                </div>
                                            ) : (
                                                <></>
                                            )}
                                        </div>
                                        <div>
                                            <div className="text-[16px] font-[600] py-[8px]">
                                                {intl.formatMessage({
                                                    id: 'app.summaryhistory.results',
                                                })}
                                                :
                                            </div>
                                            <div className="p-[12px]  bg-[#F7F7F7]">
                                                {logDetail?.target_run?.agent_id != 0 ? (
                                                    <div className="p-[12px]  bg-[#F7F7F7] leading-[22px]">
                                                        <ReactMarkdown
                                                            rehypePlugins={[rehypeHighlight]}
                                                        >
                                                            {logDetail?.target_run?.outputs?.value}
                                                        </ReactMarkdown>
                                                    </div>
                                                ) : (
                                                    <Graphic
                                                        status={logDetail?.target_run?.status}
                                                        icon={logDetail?.target_run?.icon}
                                                        title={logDetail?.target_run?.name}
                                                        textDetails={
                                                            <ProgressContainer
                                                                progressObj={{
                                                                    created_time:
                                                                    logDetail?.target_run
                                                                            ?.created_time,
                                                                    elapsed_time:
                                                                    logDetail?.target_run
                                                                            ?.elapsed_time,
                                                                    app_name:
                                                                    logDetail?.target_run?.app.name,
                                                                    status: logDetail?.target_run
                                                                        ?.status,
                                                                }}
                                                            ></ProgressContainer>
                                                        }
                                                        handleClick={() => {
                                                            setRunPanelLogRecord({
                                                                app_id: logDetail?.target_run?.app
                                                                    ?.id,
                                                                app_name:
                                                                logDetail?.target_run?.app?.name,
                                                                icon: logDetail?.target_run?.icon,
                                                                workflow_id:
                                                                logDetail?.target_run
                                                                        ?.workflow_id,
                                                                type: 2,
                                                                app_run_id:
                                                                logDetail?.target_run?.id,
                                                                run_name:
                                                                logDetail?.target_run?.name,
                                                                status: logDetail?.target_run
                                                                    ?.status,
                                                                created_time:
                                                                logDetail?.target_run
                                                                        ?.created_time,
                                                                elapsed_time:
                                                                logDetail?.target_run
                                                                        ?.elapsed_time,
                                                                completed_progress: `${logDetail?.target_run?.percentage}%`,
                                                            });
                                                        }}
                                                        progress={0 || logDetail?.target_run?.percentage}
                                                    ></Graphic>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <></>
                                )}
                            </>
                        ) : null}
                    </div>
                </ProCard>
            </ResizablePanel>
        );
    },
);
