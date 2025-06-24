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
    UserOutlined
} from '@ant-design/icons';
import { MCPToolData, MCPToolStatus, getMCPToolStatus, MCPToolRuntimeData } from '../types/mcp';
import useUserStore from '@/store/user';

const { Text, Paragraph } = Typography;
const { Panel } = Collapse;

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
                return { color: 'success', text: 'Completed' };
            case MCPToolStatus.RUNNING:
                return { color: 'processing', text: 'Running' };
            case MCPToolStatus.WAITING_CONFIRMATION:
                return { color: 'warning', text: 'Waiting Confirmation' };
            case MCPToolStatus.FAILED:
                return { color: 'error', text: 'Failed' };
            default:
                return { color: 'default', text: 'Pending' };
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

const getToolType = (name: string): string => {
    if (name.includes('skill')) return 'Skill';
    if (name.includes('workflow')) return 'Workflow';
    return 'Tool';
};

export const MCPToolDisplay: FC<MCPToolDisplayProps> = ({ toolData, intl, runtimeData }) => {
    // Use runtime status if available, otherwise calculate from existing data
    const status = runtimeData?.status || getMCPToolStatus(toolData.workflow_confirmation_status, toolData.result);
    const toolType = getToolType(toolData.name);
    
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
        console.log('Todo button clicked for workflow:', workflowConfirmation);
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
                                Workflow: {workflowConfirmation.workflow_name}
                            </Text>
                            {workflowConfirmation.confirmer_name && (
                                <Text className="text-xs text-gray-600">
                                    Confirmer: {workflowConfirmation.confirmer_name}
                                </Text>
                            )}
                        </div>
                        {workflowConfirmation.show_todo_button && (
                            <Button 
                                size="small" 
                                type="primary"
                                onClick={handleTodoButtonClick}
                            >
                                Handle Todo
                            </Button>
                        )}
                    </div>
                    <div className="mt-1 text-xs text-gray-600">
                        Status: {workflowConfirmation.status} | 
                        App Run ID: {workflowConfirmation.app_run_id} | 
                        Node Exec ID: {workflowConfirmation.node_exec_id}
                        {workflowConfirmation.need_user_confirm && (
                            <span className="ml-2 text-orange-600">
                                Requires User Confirmation
                            </span>
                        )}
                    </div>
                </div>
            )}

            {errorMessage && (
                <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-600">
                    <Text type="danger" className="text-xs">
                        Error: {errorMessage}
                    </Text>
                </div>
            )}

            <Collapse size="small" ghost>
                {(runtimeData?.args || toolData.args) && Object.keys(runtimeData?.args || toolData.args).length > 0 && (
                    <Panel header="Parameters" key="params">
                        <div className="bg-gray-50 p-2 rounded text-xs">
                            <pre className="whitespace-pre-wrap m-0 font-mono">
                                {formatJSONData(runtimeData?.args || toolData.args)}
                            </pre>
                        </div>
                    </Panel>
                )}

                {resultData && (
                    <Panel header="Result" key="result">
                        <div className={`p-2 rounded text-xs ${
                            status === MCPToolStatus.FAILED ? 'bg-red-50' : 'bg-green-50'
                        }`}>
                            <pre className="whitespace-pre-wrap m-0 font-mono">
                                {formatJSONData(resultData)}
                            </pre>
                        </div>
                    </Panel>
                )}

                {workflowConfirmation && (
                    <Panel header="Workflow Details" key="workflow">
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