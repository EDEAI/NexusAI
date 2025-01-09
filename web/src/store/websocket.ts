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

type MessageType = 'workflow_run_debug' | 'workflow_run_progress' | 'workflow_need_human_confirm' | 'generate_agent_batch';

type TypedMessageMap = {
    workflow_run_debug: WorkflowRunDebug[];
    workflow_run_progress: WorkflowRunProgress[];
    workflow_need_human_confirm: WorkflowNeedHumanConfirm[];
    generate_agent_batch: any[]; // 可以根据需要定义具体类型
    [key: string]: any[]; // 支持动态添加新类型
};

interface FlowState {
    flowMessage: any[];
    typedMessages: Partial<TypedMessageMap>;
    dealtWithData: any;
    setDealtWithData: (value: any) => void;
    addFlowMessage: (message: any) => void;
    setFlowMessage: (message: any[]) => void;
    getMessage: () => any[];
    getTypedMessages: <T extends MessageType>(type: T) => Partial<TypedMessageMap>[T] | [];
    filterMessages: (type: string, filterData?: any) => any[];
    fuzzyFilterMessages: (typePattern: string) => any[];
}

const useSocketStore = create(
    devtools<FlowState>(
        (set, get) => ({
            flowMessage: [],
            typedMessages: {},
            dealtWithData: null,
            setDealtWithData: (value: any) => {
                set({ dealtWithData: value });
            },
            addFlowMessage: message => {
                set(state => {
                    const newFlowMessage = [...state.flowMessage, message];
                    const type = message.type as MessageType;
                    
                    return {
                        flowMessage: newFlowMessage,
                        typedMessages: {
                            ...state.typedMessages,
                            [type]: [...(state.typedMessages[type] || []), message]
                        }
                    };
                });
            },
            setFlowMessage: message => {
                set(state => {
                 
                    const typedMessages = message.reduce((acc, msg) => {
                        const type = msg.type as MessageType;
                        return {
                            ...acc,
                            [type]: [...(acc[type] || []), msg]
                        };
                    }, {} as TypedMessageMap);
                    
                    return {
                        flowMessage: message,
                        typedMessages
                    };
                });
            },
            getTypedMessages: type => {
                return get().typedMessages[type] || [];
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
            fuzzyFilterMessages: (typePattern) => {
                return get().flowMessage.filter(item => 
                    item.type?.toLowerCase().includes(typePattern.toLowerCase())
                );
            },
        }),
        { name: 'useSocketStore' },
    ),
);
useSocketStore.subscribe(e => {
    console.log('socket store change', e.flowMessage);
});
export default createSelectors(useSocketStore);
