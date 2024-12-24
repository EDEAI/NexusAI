/*
 * @LastEditors: biz
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { createSelectors } from './createSelectors';

interface CommonData {
    /** Application ID corresponding to the workflow */
    app_id: number;
    /** Workflow ID */
    workflow_id: number;
    /** Workflow run process ID */
    app_run_id: number;
    /** Run type 1: Debug run 2: Formal run */
    type: number;
}

interface NodeExecData {
    /** Node execution record ID */
    node_exec_id: number;
    /** Level corresponding to the node */
    level: number;
    /** Entry edge ID corresponding to the node */
    edge_id: string;
    /** Previous node ID */
    pre_node_id: string;
    /** Current node ID */
    node_id: string;
    /** Node type */
    node_type: string;
    /** Node name */
    node_name: string;
    /** Run status 0: Not runnable 1: Runnable 2: Running 3: Run successful 4: Run failed */
    status: number;
    /** Error content when run fails, null if no error */
    error: string | null;
    /** Object data corresponding to input variables, null if no input */
    inputs: object | null;
    /** Message records of conversation with LLM model */
    messages: [string, MessageObject][];
    /** Run completion time */
    finished_time: string;
    /** Time taken for the run process */
    elapsed_time: number;
    /** Output type, can be ignored */
    output_type: number;
    /** Object data corresponding to output variables */
    outputs: OutputObject;
    /** Input tokens generated during the run process with the LLM model */
    prompt_tokens: number;
    /** Output tokens generated during the run process with the LLM model */
    completion_tokens: number;
    /** Total tokens generated during the run process with the LLM model (input + output) */
    total_tokens: number;
    /** Tokens generated during the run process with the embedding model */
    embedding_tokens: number;
    /** Tokens generated during the run process with the reranking model */
    reranking_tokens: number;
}

interface MessageObject {
    /** Variable name */
    name: string;
    /** Variable type */
    type: string;
    /** Variable value */
    value: string;
    /** Maximum length of the variable */
    max_length: number;
}

interface OutputObject {
    /** Output variable name */
    name: string;
    /** Output variable type */
    type: string;
    /** Output variable value */
    value: string;
    /** Maximum length of the output variable */
    max_length: number;
}

// Define the data structure for each message type
interface WorkflowRunDebugData extends CommonData {
    /** Current level the workflow is running at */
    level: number;
    /** Run status 1: Running 2: Run successful 3: Run failed */
    status: number;
    /** Error content when run fails */
    error: string | null;
    /** Number of completed steps */
    completed_steps: number;
    /** Whether manual confirmation is needed 0: No 1: Yes */
    need_human_confirm: number;
    /** Total time taken for the run process */
    elapsed_time: number;
    /** Input tokens generated during the entire run process with the LLM model */
    prompt_tokens: number;
    /** Output tokens generated during the entire run process with the LLM model */
    completion_tokens: number;
    /** Total tokens generated during the entire run process with the LLM model (input + output) */
    total_tokens: number;
    /** Tokens generated during the entire run process with the embedding model */
    embedding_tokens: number;
    /** Tokens generated during the entire run process with the reranking model */
    reranking_tokens: number;
    /** Total number of steps in the workflow */
    total_steps: number;
    /** Workflow overall run completion time */
    finished_time: string;
    /** Specific node data currently */
    node_exec_data: NodeExecData;
}

interface WorkflowRunProgressData extends CommonData {
    /** Workflow name */
    app_name: string;
    /** Workflow process name */
    run_name: string;
    /** Run status 1: Running 2: Run successful 3: Run failed */
    status: number;
    /** Workflow process creation time */
    created_time: string;
    /** Time taken for the process run */
    elapsed_time: number;
    /** Process run progress (percentage) */
    completed_progress: string;
}

interface WorkflowNeedHumanConfirmData extends CommonData {
    /** Workflow name */
    app_name: string;
    /** Workflow process name */
    run_name: string;
    /** Specific node data currently */
    node_exec_data: {
        /** Node execution record ID */
        node_exec_id: number;
        /** Level corresponding to the node */
        level: number;
        /** Entry edge ID corresponding to the node */
        edge_id: string;
        /** Current node ID */
        node_id: string;
        /** Node type */
        node_type: string;
        /** Node name */
        node_name: string;
    };
}

// Define the top-level interface for messages
interface WorkflowRunDebug {
    /** Message type */
    type: 'workflow_run_debug';
    /** Message data */
    data: WorkflowRunDebugData;
}

interface WorkflowRunProgress {
    /** Message type */
    type: 'workflow_run_progress';
    /** Message data */
    data: WorkflowRunProgressData;
}

interface WorkflowNeedHumanConfirm {
    /** Message type */
    type: 'workflow_need_human_confirm';
    /** Message data */
    data: WorkflowNeedHumanConfirmData;
}

type FlowMessage = WorkflowRunDebug | WorkflowRunProgress | WorkflowNeedHumanConfirm;

type FlowState = {
    flowMessage: FlowMessage[];
    dealtWithData: any;
    setDealtWithData: (value: any) => void;
    addFlowMessage: (message: FlowMessage) => void;
    setFlowMessage: (message: FlowMessage[]) => void;
    getMessage: () => FlowMessage[];
    getDebugMessage: (filterData?: Partial<WorkflowRunDebugData>) => WorkflowRunDebug[];
    getProgressMessage: (filterData?: Partial<WorkflowRunProgressData>) => WorkflowRunProgress[];
    getNeedHumanConfirmMessage: (
        filterData?: Partial<WorkflowNeedHumanConfirmData>,
    ) => WorkflowNeedHumanConfirm[];
    filterMessages: (
        type: FlowMessage['type'],
        filterData?: Partial<
            WorkflowRunDebugData | WorkflowRunProgressData | WorkflowNeedHumanConfirmData
        >,
    ) => FlowMessage[];
};

const useSocketStore = create(
    devtools<FlowState>(
        (set, get) => ({
            flowMessage: [],
            dealtWithData: null,
            setDealtWithData: (value: any) => {
                set({ dealtWithData: value });
            },
            addFlowMessage: message => {
                set({ flowMessage: [...get().flowMessage, message] });
            },
            setFlowMessage: message => {
                set({ flowMessage: message });
            },
            getMessage: () => {
                return get().flowMessage;
            },
            filterMessages: (type, filterData) => {
                let messageList = get().flowMessage.filter(item => item.type === type);
                if (filterData) {
                    messageList = messageList.filter(message => {
                        return Object.keys(filterData).every(key => {
                            return (filterData as any)[key] === (message.data as any)[key];
                        });
                    });
                }

                return messageList;
            },
            getDebugMessage: filterData => {
                return get().filterMessages('workflow_run_debug', filterData) as WorkflowRunDebug[];
            },
            getProgressMessage: filterData => {
                return get().filterMessages(
                    'workflow_run_progress',
                    filterData,
                ) as WorkflowRunProgress[];
            },
            getNeedHumanConfirmMessage: filterData => {
                return get().filterMessages(
                    'workflow_need_human_confirm',
                    filterData,
                ) as WorkflowNeedHumanConfirm[];
            },
        }),
        { name: 'useSocketStore' },
    ),
);
useSocketStore.subscribe(e => {
    console.log('socket store change', e.flowMessage);
});
export default createSelectors(useSocketStore);
