/*
 * @LastEditors: biz
 */

export interface MCPToolData {
    name: string;
    skill_or_workflow_name: string;
    workflow_run_id: number;
    workflow_confirmation_status: WorkflowConfirmationStatus | null;
    args: {
        input_variables?: Record<string, any>;
        node_confirm_users?: Record<string, any>;
        [key: string]: any;
    };
    result: any;
    id?: string | number;
    files_to_upload?: import('./fileUpload').FileToUpload[];
}

export interface WorkflowConfirmationStatus {
    id: number;
    status: string;
    app_run_id: number;
    node_exec_id: number;
    workflow_name: string;
    need_user_confirm: boolean;
    show_todo_button: boolean;
    confirmer_name?: string;
}

export interface MCPToolRuntimeData extends MCPToolData {
    id: string | number;
    status: MCPToolStatus;
    workflow_confirmation?: WorkflowConfirmationStatus;
    isWorkflow?: boolean;
    files_to_upload?: import('./fileUpload').FileToUpload[];
    uploaded_files?: import('./fileUpload').FileToUpload[];
    error?: string;
}

export interface ContentBlock {
    type: 'text' | 'mcp-tool';
    content: string;
    toolData?: MCPToolData;
}

export interface ParsedMCPContent {
    blocks: ContentBlock[];
    hasMCPTools: boolean;
}

export enum MCPToolStatus {
    PENDING = 'pending',
    RUNNING = 'running', 
    COMPLETED = 'completed',
    FAILED = 'failed',
    WAITING_CONFIRMATION = 'waiting_confirmation',
    WAITING_FILE_UPLOAD = 'waiting_file_upload'
}

export const getMCPToolStatus = (
    confirmationStatus: WorkflowConfirmationStatus | null, 
    result: any
): MCPToolStatus => {
    // If there's a workflow confirmation status, check its status
    if (confirmationStatus) {
        if (confirmationStatus.status === 'waiting_confirm') {
            return MCPToolStatus.WAITING_CONFIRMATION;
        }
        // If confirmation exists but not waiting, it's running
        if (result === null) {
            return MCPToolStatus.RUNNING;
        }
    }
    
    // Check result status
    if (result !== null) {
        // Check if result indicates failure
        if (typeof result === 'string') {
            try {
                const parsedResult = JSON.parse(result);
                if (parsedResult.status === 'failed') {
                    return MCPToolStatus.FAILED;
                }
            } catch {
                // If result is not JSON, assume it's successful
            }
        } else if (typeof result === 'object' && result.status === 'failed') {
            return MCPToolStatus.FAILED;
        }
        return MCPToolStatus.COMPLETED;
    }
    
    // Default states
    if (confirmationStatus === null && result === null) {
        return MCPToolStatus.PENDING;
    }
    
    return MCPToolStatus.PENDING;
}; 