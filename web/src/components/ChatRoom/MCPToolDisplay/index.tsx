/*
 * @LastEditors: biz
 */
import React, { FC } from 'react';
import { Card, Tag, Collapse, Typography, Button } from 'antd';
import { 
    CheckCircleOutlined, 
    LoadingOutlined, 
    ClockCircleOutlined, 
    ExclamationCircleOutlined,
    ToolOutlined,
    UserOutlined,
    FileOutlined,
    FileExcelOutlined,
    FileWordOutlined,
    FilePdfOutlined,
    FileImageOutlined,
    DownloadOutlined
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import { MCPToolData, MCPToolStatus, getMCPToolStatus, MCPToolRuntimeData } from '../types/mcp';
import { createRenderers } from '../MarkdownRenderer';
import useUserStore from '@/store/user';

const { Text, Paragraph } = Typography;
const { Panel } = Collapse;

// MCP File Item interface
interface MCPFileItem {
    file_name: string;
    file_path: string;
    variable_name?: string;
}

// Get file icon based on file extension
const getFileIcon = (fileName: string) => {
    const ext = fileName.toLowerCase().split('.').pop();
    const iconClass = "text-sm";
    switch (ext) {
        case 'xlsx':
        case 'xls':
        case 'csv':
            return <FileExcelOutlined className={`text-green-600 ${iconClass}`} />;
        case 'doc':
        case 'docx':
            return <FileWordOutlined className={`text-blue-600 ${iconClass}`} />;
        case 'pdf':
            return <FilePdfOutlined className={`text-red-600 ${iconClass}`} />;
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
        case 'svg':
            return <FileImageOutlined className={`text-purple-600 ${iconClass}`} />;
        default:
            return <FileOutlined className={`text-gray-600 ${iconClass}`} />;
    }
};

// MCP File List Component
const MCPFileList: FC<{ fileList: MCPFileItem[]; intl: any }> = ({ fileList, intl }) => {
    const handleDownload = (filePath: string, fileName: string) => {
        try {
            const link = document.createElement('a');
            link.href = filePath;
            link.download = fileName;
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (e) {
            console.error('Download file failed', e);
        }
    };

    if (!fileList || fileList.length === 0) {
        return null;
    }

    return (
        <div className="space-y-1">
            {fileList.map((file, index) => (
                <div key={index} className="mb-2 last:mb-0">
                    {file.variable_name && (
                        <div className="mb-1">
                            <Text strong className="text-xs text-gray-700">
                                {file.variable_name}:
                            </Text>
                        </div>
                    )}
                    <div className="bg-green-50 border-l-4 border-l-green-400 border border-green-200 rounded p-2 hover:bg-green-100 transition-all duration-200">
                        <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2 flex-1 min-w-0">
                                <div className="flex-shrink-0">
                                    {getFileIcon(file.file_name)}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="text-xs text-gray-800 truncate font-mono">
                                        {file.file_name}
                                    </div>
                                </div>
                            </div>
                            <Button
                                type="text"
                                size="small"
                                icon={<DownloadOutlined />}
                                onClick={() => handleDownload(file.file_path, file.file_name)}
                                className="flex-shrink-0 text-green-600 hover:text-green-800 hover:bg-green-200 rounded transition-colors duration-200"
                                title={intl.formatMessage({ id: 'app.chatroom.mcptool.downloadFile' })}
                            />
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

interface MCPToolDisplayProps {
    toolData: MCPToolData;
    intl: any;
    runtimeData?: MCPToolRuntimeData | null;
}

const StatusIcon: FC<{ status: MCPToolStatus }> = ({ status }) => {
    switch (status) {
        case MCPToolStatus.COMPLETED:
            return <CheckCircleOutlined className="text-green-500" />;
        case MCPToolStatus.RUNNING:
            return <LoadingOutlined className="text-blue-500" />;
        case MCPToolStatus.WAITING_CONFIRMATION:
            return <ClockCircleOutlined className="text-orange-500" />;
        case MCPToolStatus.FAILED:
            return <ExclamationCircleOutlined className="text-red-500" />;
        default:
            return <ClockCircleOutlined className="text-gray-500" />;
    }
};

const StatusTag: FC<{ status: MCPToolStatus; intl: any }> = ({ status, intl }) => {
    const getStatusConfig = (status: MCPToolStatus) => {
        switch (status) {
            case MCPToolStatus.COMPLETED:
                return { color: 'success', text: intl.formatMessage({ id: 'app.chatroom.mcptool.status.completed' }) };
            case MCPToolStatus.RUNNING:
                return { color: 'processing', text: intl.formatMessage({ id: 'app.chatroom.mcptool.status.running' }) };
            case MCPToolStatus.WAITING_CONFIRMATION:
                return { color: 'warning', text: intl.formatMessage({ id: 'app.chatroom.mcptool.status.waiting' }) };
            case MCPToolStatus.FAILED:
                return { color: 'error', text: intl.formatMessage({ id: 'app.chatroom.mcptool.status.failed' }) };
            default:
                return { color: 'default', text: intl.formatMessage({ id: 'app.chatroom.mcptool.status.pending' }) };
        }
    };

    const config = getStatusConfig(status);
    return <Tag color={config.color}>{config.text}</Tag>;
};

const formatJSONData = (data: any): string => {
    if (data === null || data === undefined) return 'null';
    if (typeof data === 'string') {
        try {
            // Try to parse and pretty-print JSON strings
            const parsed = JSON.parse(data);
            return JSON.stringify(parsed, null, 2);
        } catch {
            // If not JSON, return as is
            return data;
        }
    }
    try {
        return JSON.stringify(data, null, 2);
    } catch {
        return String(data);
    }
};

const getToolType = (name: string, intl: any): string => {
    if (name.includes('skill')) return intl.formatMessage({ id: 'app.chatroom.mcptool.type.skill' });
    if (name.includes('workflow')) return intl.formatMessage({ id: 'app.chatroom.mcptool.type.workflow' });
    return intl.formatMessage({ id: 'app.chatroom.mcptool.type.tool' });
};

// Helper function to separate special fields from regular fields
const separateSpecialFields = (args: any) => {
    if (!args || typeof args !== 'object') {
        return { 
            specialFields: {} as { input_variables?: Record<string, any> }, 
            regularFields: args 
        };
    }
    
    const specialFields: { input_variables?: Record<string, any> } = {};
    const regularFields: Record<string, any> = {};
    
    Object.keys(args).forEach(key => {
        if (key === 'input_variables') {
            specialFields[key] = args[key];
        } else {
            regularFields[key] = args[key];
        }
    });
    
    return { specialFields, regularFields };
};

// Component to render input variables as key-value list
const InputVariablesRenderer: FC<{ inputVariables: Record<string, any>; intl: any }> = ({ inputVariables, intl }) => {
    if (!inputVariables || typeof inputVariables !== 'object' || Object.keys(inputVariables).length === 0) {
        return null;
    }
    
    return (
        <div className="mb-3">
            <div className="mb-2">
                <Text strong className="text-blue-600 text-sm">
                    {intl.formatMessage({ id: 'app.chatroom.mcptool.inputVariables' })}
                </Text>
            </div>
            <div className="bg-blue-50 p-3 rounded border border-blue-200">
                {Object.entries(inputVariables).map(([key, value]) => (
                    <div key={key} className="flex items-start gap-2 mb-1 last:mb-0">
                        <Text strong className="text-xs text-gray-700 min-w-0 flex-shrink-0">
                            {key}:
                        </Text>
                        <Text className="text-xs text-gray-800 break-words flex-1 whitespace-pre-wrap">
                            {typeof value === 'string' ? value : JSON.stringify(value)}
                        </Text>
                    </div>
                ))}
            </div>
        </div>
    );
};

// Enhanced parameters display component
const EnhancedParametersDisplay: FC<{ args: any; intl: any }> = ({ args, intl }) => {
    try {
        const { specialFields, regularFields } = separateSpecialFields(args);
        const hasInputVariables = specialFields.input_variables && 
            Object.keys(specialFields.input_variables).length > 0;
        const hasRegularFields = regularFields && 
            Object.keys(regularFields).length > 0;
        
        if (!hasInputVariables && !hasRegularFields) {
            return (
                <div className="bg-gray-50 p-2 rounded text-xs text-gray-500">
                    {intl.formatMessage({ id: 'app.chatroom.mcptool.noParameters' })}
                </div>
            );
        }
        
        return (
            <div>
                {hasInputVariables && (
                    <InputVariablesRenderer inputVariables={specialFields.input_variables} intl={intl} />
                )}
                
                {hasRegularFields && (
                    <div>
                        {hasInputVariables && (
                            <div className="mb-2">
                                <Text strong className="text-gray-600 text-sm">
                                    {intl.formatMessage({ id: 'app.chatroom.mcptool.otherParameters' })}
                                </Text>
                            </div>
                        )}
                        <div className="bg-gray-50 p-2 rounded text-xs">
                            <pre className="whitespace-pre-wrap m-0 font-mono">
                                {formatJSONData(regularFields)}
                            </pre>
                        </div>
                    </div>
                )}
            </div>
        );
    } catch (error) {
        // Fallback to original JSON display if parsing fails
        console.warn('Failed to parse parameters for enhanced display:', error);
        return (
            <div className="bg-gray-50 p-2 rounded text-xs">
                <pre className="whitespace-pre-wrap m-0 font-mono">
                    {formatJSONData(args)}
                </pre>
            </div>
        );
    }
};

// Enhanced result display component
const EnhancedResultDisplay: FC<{ resultData: any; intl: any; status: MCPToolStatus }> = ({ resultData, intl, status }) => {
    // Parse result data
    let parsedResult = resultData;
    if (typeof resultData === 'string') {
        try {
            parsedResult = JSON.parse(resultData);
        } catch {
            // Keep original if not JSON
            parsedResult = resultData;
        }
    }
    
    // Check if it's a structured success result with outputs
    const isSuccessWithOutputs = parsedResult && 
        typeof parsedResult === 'object' && 
        parsedResult.status === 'success' && 
        parsedResult.outputs && 
        typeof parsedResult.outputs === 'object';
    
    if (isSuccessWithOutputs) {
        const outputs = parsedResult.outputs;
        const fileList = parsedResult.file_list;
        const hasOutputs = Object.keys(outputs).length > 0;
        const hasFileList = fileList && Array.isArray(fileList) && fileList.length > 0;
        
        if (!hasOutputs && !hasFileList) {
            return (
                <div className="bg-green-50 p-2 rounded text-xs text-gray-500">
                    {intl.formatMessage({ id: 'app.chatroom.mcptool.noOutputs' })}
                </div>
            );
        }
        
        return (
            <div className="bg-green-50 p-3 rounded border border-green-200">
                {hasOutputs && (
                    <>
                        <div className="mb-2">
                            <Text strong className="text-green-600 text-sm">
                                {intl.formatMessage({ id: 'app.chatroom.mcptool.outputs' })}
                            </Text>
                        </div>
                        {Object.entries(outputs).map(([key, value]) => (
                            <div key={key} className="mb-3 last:mb-0">
                                <div className="mb-1">
                                    <Text strong className="text-xs text-gray-700">
                                        {key}:
                                    </Text>
                                </div>
                                <div className="bg-white p-2 rounded border border-green-300 whitespace-pre-wrap">
                                    {typeof value === 'string' ? (
                                        <ReactMarkdown
                                            rehypePlugins={[rehypeHighlight]}
                                            components={createRenderers(0, intl)}
                                            className="text-xs [&_p]:mb-1 [&_p:last-child]:mb-0 [&_pre]:text-xs [&_code]:text-xs"
                                        >
                                            {value}
                                        </ReactMarkdown>
                                    ) : (
                                        <pre className="whitespace-pre-wrap m-0 font-mono text-xs text-gray-800">
                                            {formatJSONData(value)}
                                        </pre>
                                    )}
                                </div>
                            </div>
                        ))}
                    </>
                )}
                
                {hasFileList && (
                    <div className={hasOutputs ? "mt-4" : ""}>
                        <div className="mb-2">
                            <Text strong className="text-green-600 text-sm">
                                {intl.formatMessage({ id: 'app.chatroom.mcptool.files' })}
                            </Text>
                        </div>
                        <div className="bg-white p-3 rounded border border-green-300">
                            <MCPFileList fileList={fileList} intl={intl} />
                        </div>
                    </div>
                )}
            </div>
        );
    }
    
    // Fallback to original display for failed results or other formats
    return (
        <div className={`p-2 rounded text-xs ${
            status === MCPToolStatus.FAILED ? 'bg-red-50' : 'bg-green-50'
        }`}>
            <pre className="whitespace-pre-wrap m-0 font-mono">
                {formatJSONData(resultData)}
            </pre>
        </div>
    );
};

export const MCPToolDisplay: FC<MCPToolDisplayProps> = ({ toolData, intl, runtimeData }) => {
    // Use runtime status if available, otherwise calculate from existing data
    const status = runtimeData?.status || getMCPToolStatus(toolData.workflow_confirmation_status, toolData.result);
    const toolType = getToolType(toolData.name, intl);
    
    // Get workflow confirmation from either runtime data or tool data
    const workflowConfirmation = runtimeData?.workflow_confirmation || toolData.workflow_confirmation_status;
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    
    // Parse result for error handling - use runtime result if available
    const resultData = runtimeData?.result || toolData.result;
    let errorMessage = null;
    
    if (typeof resultData === 'string') {
        try {
            const parsed = JSON.parse(resultData);
            if (parsed.status === 'failed') {
                errorMessage = parsed.message;
            }
        } catch {
            // Keep original result if not JSON
        }
    } else if (typeof resultData === 'object' && resultData?.status === 'failed') {
        errorMessage = resultData.message;
    }

    const handleTodoButtonClick = () => {
        // Handle todo button click - could navigate to workflow or open confirmation dialog
      
        // TODO: Implement navigation or confirmation dialog
        setDealtWithData({
            ...workflowConfirmation,
            exec_id: workflowConfirmation.node_exec_id
        });
    };

    return (
        <Card 
            className="mb-3 border border-gray-200 shadow-sm"
            size="small"
        >
            <div className="flex items-center gap-2 mb-2">
                <ToolOutlined className="text-blue-500" />
                <Text strong className="text-sm">
                    {runtimeData?.skill_or_workflow_name || toolData.skill_or_workflow_name}
                </Text>
                <Tag color="blue">{toolType}</Tag>
                <StatusIcon status={status} />
                <StatusTag status={status} intl={intl} />
            </div>

            {/* Workflow confirmation section */}
            {workflowConfirmation &&status !== MCPToolStatus.COMPLETED && 
                         status !== MCPToolStatus.FAILED && (
                <div className="mb-2 p-2 bg-orange-50 border border-orange-200 rounded">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <UserOutlined className="text-orange-500" />
                            <Text className="text-sm font-medium">
                                {intl.formatMessage({ id: 'app.chatroom.mcptool.workflow' })}: {workflowConfirmation.workflow_name}
                            </Text>
                            {workflowConfirmation.confirmer_name && (
                                <Text className="text-xs text-gray-600">
                                    {intl.formatMessage({ id: 'app.chatroom.mcptool.confirmer' })}: {workflowConfirmation.confirmer_name}
                                </Text>
                            )}
                        </div>
                        {workflowConfirmation.show_todo_button && (
                            <Button 
                                size="small" 
                                type="primary"
                                onClick={handleTodoButtonClick}
                            >
                                {intl.formatMessage({ id: 'app.chatroom.mcptool.handleTodo' })}
                            </Button>
                        )}
                    </div>
                 
                </div>
            )}

            {errorMessage && (
                <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-600">
                    <Text type="danger" className="text-xs">
                        {intl.formatMessage({ id: 'app.chatroom.mcptool.error' })}: {errorMessage}
                    </Text>
                </div>
            )}

            <Collapse size="small" ghost>
                {(runtimeData?.args || toolData.args) && Object.keys(runtimeData?.args || toolData.args).length > 0 && (
                    <Panel header={intl.formatMessage({ id: 'app.chatroom.mcptool.parameters' })} key="params">
                        <EnhancedParametersDisplay args={runtimeData?.args || toolData.args} intl={intl} />
                    </Panel>
                )}

                {resultData && (
                    <Panel header={intl.formatMessage({ id: 'app.chatroom.mcptool.result' })} key="result">
                        <EnhancedResultDisplay 
                            resultData={resultData} 
                            intl={intl} 
                            status={status} 
                        />
                    </Panel>
                )}

                {workflowConfirmation && (
                    <Panel header={intl.formatMessage({ id: 'app.chatroom.mcptool.workflowDetails' })} key="workflow">
                        <div className="bg-blue-50 p-2 rounded text-xs">
                            <pre className="whitespace-pre-wrap m-0 font-mono">
                                {formatJSONData(workflowConfirmation)}
                            </pre>
                        </div>
                    </Panel>
                )}
            </Collapse>
        </Card>
    );
}; 