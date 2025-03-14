/*
 * @LastEditors: biz
 */
import { getAgentLogDetail } from '@/api/agents';
import ResizablePanel from '@/components/Panel/DraggablePanel';
import { CloseOutlined } from '@ant-design/icons';
import { ProCard } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useRequest } from 'ahooks';
import { Button, Descriptions, Spin, Tag, Timeline, Typography } from 'antd';
import { memo, useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import CodeEditor from '../WorkFlow/components/Editor/CodeEditor';

export default memo(
    ({ data, onClose }: { data: { app_id: string; app_run_id: string }; onClose?: () => void }) => {
        const intl = useIntl();
        const [panelWidth, setPanelWidth] = useState(500);

        const {
            data: logDetail,
            loading,
            run,
        } = useRequest(
            async (agentId, appRunId) => {
                const res = await getAgentLogDetail(agentId, appRunId);
                return res.data;
            },
            {
                manual: true,
            },
        );

        useEffect(() => {
            if (data?.app_id && data?.app_run_id) {
                run(data.app_id, data.app_run_id);
            }
        }, [data?.app_id, data?.app_run_id, run]);

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
                            {intl.formatMessage({ id: 'agent.log.detail' })}
                        </Typography.Title>
                    }
                    loading={loading}
                >
                    <div className="space-y-6">
                        {loading ? (
                            <div className="flex items-center justify-center h-40">
                                <Spin />
                            </div>
                        ) : logDetail ? (
                            <>
                                <Descriptions column={1} bordered size="small">
                                    <Descriptions.Item
                                        label={intl.formatMessage({ id: 'workflow.user' })}
                                    >
                                        {logDetail.nickname}
                                    </Descriptions.Item>
                                    <Descriptions.Item
                                        label={intl.formatMessage({ id: 'workflow.status' })}
                                    >
                                        {getStatusTag(logDetail.status)}
                                    </Descriptions.Item>
                                    <Descriptions.Item
                                        label={intl.formatMessage({ id: 'workflow.created_time' })}
                                    >
                                        {logDetail.created_time}
                                    </Descriptions.Item>
                                    <Descriptions.Item
                                        label={intl.formatMessage({ id: 'workflow.elapsed_time' })}
                                    >
                                        {logDetail.elapsed_time}s
                                    </Descriptions.Item>
                                    <Descriptions.Item label="Tokens">
                                        {logDetail.total_tokens}
                                    </Descriptions.Item>
                                </Descriptions>

                                <div className="mt-4">
                                    <Typography.Title level={5}>
                                        {intl.formatMessage({ id: 'agent.log.output' })}
                                    </Typography.Title>
                                    {logDetail.outputs ? (
                                        <div>
                                            {logDetail?.outputs?.type == 'json' ? (
                                                <div className="h-80">
                                                    <CodeEditor
                                                        language="python3"
                                                        value={
                                                            JSON.parse(logDetail.outputs?.value) ||
                                                            '{}'
                                                        }
                                                        readOnly
                                                        isJSONStringifyBeauty
                                                        onChange={() => {}}
                                                        title={`JSON`}
                                                    />
                                                </div>
                                            ) : (
                                                <div className="bg-gray-50 p-4 rounded mt-2">
                                                    <ReactMarkdown
                                                        rehypePlugins={[rehypeHighlight]}
                                                    >
                                                        {logDetail.outputs?.value || ''}
                                                    </ReactMarkdown>
                                                </div>
                                            )}
                                        </div>
                                    ) : logDetail.error ? (
                                        <div className="bg-gray-50 p-4 rounded mt-2 border-l-4 border-red-500">
                                            <div className="text-red-500 font-medium mb-2">
                                                {intl.formatMessage({ id: 'agent.log.error' })}
                                            </div>
                                            <pre className="whitespace-pre-wrap text-sm text-red-500">
                                                {logDetail.error}
                                            </pre>
                                        </div>
                                    ) : (
                                        <div className="bg-gray-50 p-4 rounded mt-2">
                                            <div className="text-sm text-gray-500">
                                                {intl.formatMessage({ id: 'agent.log.no.output' })}
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {Array.isArray(logDetail?.prompt_data) &&
                                    logDetail.prompt_data.length > 0 && (
                                        <div className="mt-4">
                                            <Typography.Title level={5}>
                                                {intl.formatMessage({
                                                    id: 'agent.log.conversation',
                                                })}
                                            </Typography.Title>
                                            <Timeline className="mt-2">
                                                {logDetail.prompt_data.map((item, index) => {
                                                    const [role, content] = item;
                                                    return (
                                                        <Timeline.Item
                                                            key={index}
                                                            color={
                                                                role === 'human' ? 'blue' : 'green'
                                                            }
                                                        >
                                                            <div className="bg-gray-50 p-3 rounded">
                                                                <div className="text-xs text-gray-500 mb-1">
                                                                    {role}
                                                                </div>
                                                                <div className="text-sm whitespace-pre-wrap">
                                                                    {content.value}
                                                                </div>
                                                            </div>
                                                        </Timeline.Item>
                                                    );
                                                })}
                                            </Timeline>
                                        </div>
                                    )}
                            </>
                        ) : null}
                    </div>
                </ProCard>
            </ResizablePanel>
        );
    },
);
