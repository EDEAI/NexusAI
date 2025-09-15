/*
 * @LastEditors: biz
 */
import { getAgentLogDetail } from '@/api/agents';
import ResizablePanel from '@/components/Panel/DraggablePanel';
import { CloseOutlined, DownloadOutlined, FileOutlined, ToolOutlined } from '@ant-design/icons';
import { ProCard } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useRequest } from 'ahooks';
import { Button, Card, Collapse, Descriptions, Spin, Tag, Timeline, Typography } from 'antd';
import { memo, useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import CodeEditor from '../WorkFlow/components/Editor/CodeEditor';

const { Panel } = Collapse;
const { Text } = Typography;

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
                                    {logDetail.error ? (
                                        <div className="bg-gray-50 p-4 rounded mt-2 border-l-4 border-red-500">
                                            <div className="text-red-500 font-medium mb-2">
                                                {intl.formatMessage({ id: 'agent.log.error' })}
                                            </div>
                                            <pre className="whitespace-pre-wrap text-sm text-red-500">
                                                {logDetail.error}
                                            </pre>
                                        </div>
                                    ) : (logDetail.outputs && logDetail.outputs.value !== undefined && logDetail.outputs.value !== null && logDetail.outputs.value !== '') ? (
                                        <div>
                                            {logDetail?.outputs?.type == 'json' ? (
                                                (() => {
                                                    // First check if value is string or json, parse as json if it's string
                                                    let parsedValue;
                                                    try {
                                                        parsedValue = typeof logDetail.outputs?.value === 'string' 
                                                            ? JSON.parse(logDetail.outputs.value) 
                                                            : logDetail.outputs?.value;
                                                    } catch (error) {
                                                        // Parse failed, use original logic
                                                        return (
                                                            <div className="h-80">
                                                                <CodeEditor
                                                                    language="python3"
                                                                    value={
                                                                        JSON.parse(logDetail.outputs?.value || '{}') ||
                                                                         '{}'
                                                                    }
                                                                    readOnly
                                                                    isJSONStringifyBeauty
                                                                    onChange={() => {}}
                                                                    title={`JSON`}
                                                                />
                                                            </div>
                                                        );
                                                    }
                                                    
                                                    // Check if value is array
                                                    if (Array.isArray(parsedValue)) {
                                                        // First apply existing mcp_tool_use_records logic
                                                        if (Array.isArray(logDetail.mcp_tool_use_records) && 
                                                            logDetail.mcp_tool_use_records.length > 0) {
                                                            // Iterate through value to find first element with type 'text'
                                                            const textItem = parsedValue.find(item => item.type === 'text');
                                                            if (textItem && textItem.text) {
                                                                const textContent = typeof textItem.text === 'string' 
                                                                    ? textItem.text 
                                                                    : JSON.stringify(textItem.text, null, 2);
                                                                return (
                                                                    <div className="bg-gray-50 p-4 rounded mt-2">
                                                                        <ReactMarkdown
                                                                            rehypePlugins={[rehypeHighlight]}
                                                                        >
                                                                            {textContent}
                                                                        </ReactMarkdown>
                                                                    </div>
                                                                );
                                                            }
                                                        }
                                                        
                                                        // If mcp_tool_use_records condition not met, check if value has only one element
                                                        if (parsedValue.length === 1) {
                                                            const singleItem = parsedValue[0];
                                                            // Check if this element has both type and text properties, and type equals 'text'
                                                            if (singleItem && 
                                                                singleItem.type === 'text' && 
                                                                singleItem.text !== undefined) {
                                                                const textContent = typeof singleItem.text === 'string' 
                                                                    ? singleItem.text 
                                                                    : JSON.stringify(singleItem.text, null, 2);
                                                                return (
                                                                    <div className="bg-gray-50 p-4 rounded mt-2">
                                                                        <ReactMarkdown
                                                                            rehypePlugins={[rehypeHighlight]}
                                                                        >
                                                                            {textContent}
                                                                        </ReactMarkdown>
                                                                    </div>
                                                                );
                                                            }
                                                        }
                                                    }
                                                    
                                                    // If above conditions not met, use original logic
                                                    return (
                                                        <div className="h-80">
                                                            <CodeEditor
                                                                language="python3"
                                                                value={
                                                                    JSON.parse(logDetail.outputs?.value || '{}') ||
                                                                     '{}'
                                                                }
                                                                readOnly
                                                                isJSONStringifyBeauty
                                                                onChange={() => {}}
                                                                title={`JSON`}
                                                            />
                                                        </div>
                                                    );
                                                })()
                                            ) : (
                                                <div className="bg-gray-50 p-4 rounded mt-2">
                                                    <ReactMarkdown
                                                        rehypePlugins={[rehypeHighlight]}
                                                    >
                                                        {typeof logDetail.outputs?.value === 'string' 
                                                            ? logDetail.outputs.value 
                                                            : JSON.stringify(logDetail.outputs?.value ?? '', null, 2)}
                                                    </ReactMarkdown>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="bg-gray-50 p-4 rounded mt-2">
                                            <div className="text-sm text-gray-500">
                                                {intl.formatMessage({ id: 'agent.log.no.output' })}
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {Array.isArray(logDetail?.mcp_tool_use_records) &&
                                    logDetail.mcp_tool_use_records.length > 0 && (
                                        <div className="mt-4">
                                            <Typography.Title level={5}>
                                                {intl.formatMessage({ id: 'app.chatroom.mcptool.toolCalls' })}
                                            </Typography.Title>
                                            <div className="space-y-3 mt-2">
                                                {logDetail.mcp_tool_use_records.map((toolRecord, index) => {
                                                    const toolType = toolRecord.name?.startsWith('nexusai__workflow') 
                                                        ? intl.formatMessage({ id: 'app.chatroom.mcptool.type.workflow' })
                                                        : toolRecord.name?.startsWith('nexusai__skill')
                                                        ? intl.formatMessage({ id: 'app.chatroom.mcptool.type.skill' })
                                                        : intl.formatMessage({ id: 'app.chatroom.mcptool.type.tool' });
                                                    
                                                    return (
                                                        <Card key={index} className="border border-gray-200 shadow-sm" size="small">
                                                            <div className="flex items-center gap-2 mb-2">
                                                                <ToolOutlined className="text-blue-500" />
                                                                <Text strong className="text-sm">
                                                                    {toolRecord.skill_or_workflow_name}
                                                                </Text>
                                                                <Tag color="blue">{toolType}</Tag>
                                                            </div>
                                                            
                                                            <Collapse size="small" ghost>
                                                                {toolRecord.args?.input_variables && 
                                                                    Object.keys(toolRecord.args.input_variables).length > 0 && (
                                                                    <Panel 
                                                                        header={intl.formatMessage({ id: 'app.chatroom.mcptool.inputVariables' })} 
                                                                        key="inputVariables"
                                                                    >
                                                                        <div className="bg-gray-50 p-3 rounded">
                                                                            <pre className="text-sm whitespace-pre-wrap">
                                                                                {JSON.stringify(toolRecord.args.input_variables, null, 2)}
                                                                            </pre>
                                                                        </div>
                                                                        
                                                                        {Array.isArray(toolRecord.files_to_upload) && 
                                                                            toolRecord.files_to_upload.filter(file => file && file.file_path && file.file_path.trim() !== '').length > 0 && (
                                                                            <div className="mt-3">
                                                                                <Text strong className="text-sm block mb-2">
                                                                                    {intl.formatMessage({ id: 'app.chatroom.mcptool.inputFiles' })}
                                                                                </Text>
                                                                                <div className="space-y-2">
                                                                                    {toolRecord.files_to_upload
                                                                                        .filter(file => file && file.file_path && file.file_path.trim() !== '')
                                                                                        .map((file, fileIndex) => (
                                                                                        <div key={fileIndex} className="flex items-center justify-between p-2 bg-white border border-gray-200 rounded">
                                                                                            <div className="flex items-center gap-2">
                                                                                                <FileOutlined className="text-gray-500" />
                                                                                                <div>
                                                                                                    <div className="text-sm font-medium">
                                                                                                        {file.variable_name || file.file_name}
                                                                                                    </div>
                                                                                                </div>
                                                                                            </div>
                                                                                            <Button
                                                                                                type="text"
                                                                                                size="small"
                                                                                                icon={<DownloadOutlined />}
                                                                                                onClick={() => {
                                                                                                    const link = document.createElement('a');
                                                                                                    link.href = file.file_path;
                                                                                                    link.download = file.file_name;
                                                                                                    link.target = '_blank';
                                                                                                    document.body.appendChild(link);
                                                                                                    link.click();
                                                                                                    document.body.removeChild(link);
                                                                                                }}
                                                                                                className="text-green-600 hover:text-green-800 hover:bg-green-200"
                                                                                                title={intl.formatMessage({ id: 'app.chatroom.mcptool.downloadFile' })}
                                                                                            />
                                                                                        </div>
                                                                                    ))}
                                                                                </div>
                                                                            </div>
                                                                        )}
                                                                    </Panel>
                                                                )}
                                                                
                                                                {toolRecord.result && (
                                                                    <Panel 
                                                                        header={intl.formatMessage({ id: 'app.chatroom.mcptool.result' })} 
                                                                        key="result"
                                                                    >
                                                                        {(() => {
                                                                            const isWorkflowOrSkill = toolRecord.name?.startsWith('nexusai__workflow') || toolRecord.name?.startsWith('nexusai__skill');
                                                                            
                                                                            if (!isWorkflowOrSkill) {
                                                                                return (
                                                                                    <div className="bg-gray-50 p-3 rounded">
                                                                                        <pre className="text-sm whitespace-pre-wrap">
                                                                                            {typeof toolRecord.result === 'string' 
                                                                                                ? toolRecord.result 
                                                                                                : JSON.stringify(toolRecord.result, null, 2)
                                                                                            }
                                                                                        </pre>
                                                                                    </div>
                                                                                );
                                                                            }
                                                                            
                                                                            try {
                                                                                const resultObj = typeof toolRecord.result === 'string' 
                                                                                    ? JSON.parse(toolRecord.result) 
                                                                                    : toolRecord.result;
                                                                                
                                                                                const isSuccess = resultObj.status === 'success';
                                                                                const isFailed = resultObj.status === 'failed';
                                                                                
                                                                                return (
                                                                                    <div className="space-y-3">
                                                                                        <div className={`p-3 rounded flex items-center gap-2 ${
                                                                                            isSuccess ? 'bg-green-50 border border-green-200' : 
                                                                                            isFailed ? 'bg-red-50 border border-red-200' : 
                                                                                            'bg-gray-50 border border-gray-200'
                                                                                        }`}>
                                                                                            <div className={`w-2 h-2 rounded-full ${
                                                                                                isSuccess ? 'bg-green-500' : 
                                                                                                isFailed ? 'bg-red-500' : 
                                                                                                'bg-gray-500'
                                                                                            }`} />
                                                                                            <Text strong className={`text-sm ${
                                                                                                isSuccess ? 'text-green-700' : 
                                                                                                isFailed ? 'text-red-700' : 
                                                                                                'text-gray-700'
                                                                                            }`}>
                                                                                                {isSuccess ? intl.formatMessage({ id: 'app.chatroom.mcptool.status.completed' }) : 
                                                                                                 isFailed ? intl.formatMessage({ id: 'app.chatroom.mcptool.status.failed' }) : 
                                                                                                 resultObj.status}
                                                                                            </Text>
                                                                                        </div>
                                                                                        
                                                                                        {isFailed && resultObj.message && (
                                                                                            <div className="bg-red-50 p-3 rounded border border-red-200">
                                                                                                <Text className="text-red-700 text-sm">
                                                                                                    {resultObj.message}
                                                                                                </Text>
                                                                                            </div>
                                                                                        )}
                                                                                        
                                                                                        {isSuccess && resultObj.outputs && (
                                                                                            <div className="bg-gray-50 p-3 rounded">
                                                                                                <Text strong className="text-sm block mb-2">
                                                                                                    {intl.formatMessage({ id: 'app.chatroom.mcptool.outputs' })}
                                                                                                </Text>
                                                                                                <pre className="text-sm whitespace-pre-wrap">
                                                                                                    {JSON.stringify(resultObj.outputs, null, 2)}
                                                                                                </pre>
                                                                                            </div>
                                                                                        )}
                                                                                        
                                                                                        {isSuccess && Array.isArray(resultObj.file_list) && resultObj.file_list.length > 0 && (
                                                                                            <div className="bg-gray-50 p-3 rounded">
                                                                                                <Text strong className="text-sm block mb-2">
                                                                                                    {intl.formatMessage({ id: 'app.chatroom.mcptool.files' })}
                                                                                                </Text>
                                                                                                <div className="space-y-2">
                                                                                                    {resultObj.file_list.map((file, fileIndex) => (
                                                                                                        <div key={fileIndex} className="flex items-center justify-between p-2 bg-white border border-gray-200 rounded">
                                                                                                            <div className="flex items-center gap-2">
                                                                                                                <FileOutlined className="text-gray-500" />
                                                                                                                <div>
                                                                                                                <div className="text-sm font-medium">
                                                                                                                    {file.variable_name || file.file_name || file.name}
                                                                                                                </div>
                                                                                                            </div>
                                                                                                            </div>
                                                                                                            {file.file_path && (
                                                                                                                <Button
                                                                                                                    type="text"
                                                                                                                    size="small"
                                                                                                                    icon={<DownloadOutlined />}
                                                                                                                    onClick={() => {
                                                                                                                        const link = document.createElement('a');
                                                                                                                        link.href = file.file_path;
                                                                                                                        link.download = file.file_name || file.name;
                                                                                                                        link.target = '_blank';
                                                                                                                        document.body.appendChild(link);
                                                                                                                        link.click();
                                                                                                                        document.body.removeChild(link);
                                                                                                                    }}
                                                                                                                    className="text-green-600 hover:text-green-800 hover:bg-green-200"
                                                                                                                    title={intl.formatMessage({ id: 'app.chatroom.mcptool.downloadFile' })}
                                                                                                                />
                                                                                                            )}
                                                                                                        </div>
                                                                                                    ))}
                                                                                                </div>
                                                                                            </div>
                                                                                        )}
                                                                                    </div>
                                                                                );
                                                                            } catch (error) {
                                                                                return (
                                                                                    <div className="bg-gray-50 p-3 rounded">
                                                                                        <pre className="text-sm whitespace-pre-wrap">
                                                                                            {typeof toolRecord.result === 'string' 
                                                                                                ? toolRecord.result 
                                                                                                : JSON.stringify(toolRecord.result, null, 2)
                                                                                            }
                                                                                        </pre>
                                                                                    </div>
                                                                                );
                                                                            }
                                                                        })()}
                                                                    </Panel>
                                                                )}
                                                            </Collapse>
                                                        </Card>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}

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
