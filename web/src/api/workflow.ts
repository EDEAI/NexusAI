/*
 * @LastEditors: biz
 */

import aniRequest from './request';

// Get agent list
// @param {number} type - Agent search type, default is 1
// @returns {Promise<any>} - Returns a Promise object with the agent list
export const getAgentList = async (type = 1) => {
    return await aniRequest<any>(`/v1/agent/agent_list`, {
        method: 'GET',
        data: {
            page_size: 999999,
            agent_search_type: type,
        },
    });
};

// Get agent information
// @param {string} app_id - Application ID of the agent
// @returns {Promise<any>} - Returns a Promise object with the agent information
export const getAgentInfo = async app_id => {
    return await aniRequest<any>(`/v1/agent/agent_info/${app_id}`, {
        method: 'GET',
        data: {
            app_id,
            publish_status: 1,
        },
    });
};

// Get vector list
// @returns {Promise<any>} - Returns a Promise object with the vector list
export const getVectorList = async (isTeam: 1 | 2 = 1) => {
    return await aniRequest<any>(`/v1/vector/dataset_list/${isTeam}`, { method: 'GET' });
};

// Get skill list
// @param {number} skill_search_type - Skill search type
// @returns {Promise<any>} - Returns a Promise object with the skill list
export const getSkillList = async skill_search_type => {
    return await aniRequest<any>(`/v1/skill/skill_list`, {
        method: 'GET',
        data: {
            skill_search_type,
            page: 1,
            page_size: 999999,
        },
    });
};

// Get skill information
// @param {string} app_id - Application ID of the skill
// @returns {Promise<any>} - Returns a Promise object with the skill information
export const getSkillInfo = async app_id => {
    return await aniRequest<any>(`/v1/skill/skill_info/${app_id}`, {
        method: 'GET',
        data: {
            app_id,
            publish_status: 1,
        },
    });
};

// Get tools list
// @returns {Promise<any>} - Returns a Promise object with the tools list
export const getToolsList = async () => {
    return await aniRequest<any>(`/v1/tool/tools`, { method: 'GET' });
};

// Get model list
// @returns {Promise<any>} - Returns a Promise object with the model list
export const getModelList = async () => {
    return await aniRequest<any>(`/v1/llm/llm_model_list`, { method: 'GET' });
};

// Update workflow
// @param {string} app_id - Application ID of the workflow
// @param {object} graph - Graph data of the workflow
// @returns {Promise<any>} - Returns a Promise object with the update result
export const updateWorkFlow = async (app_id, data) => {
    if (!app_id) return;
    return await aniRequest<any>(`/v1/workflow/workflow_app_update/${app_id}`, {
        method: 'PUT',
        data,
    });
};

// Get workflow information
// @param {string} app_id - Application ID of the workflow
// @returns {Promise<any>} - Returns a Promise object with the workflow information
export const getWorkFlowInfo = async (app_id, publish_status: number | string = 0) => {
    return await aniRequest<any>(`/v1/workflow/workflows_info/${app_id}`, {
        method: 'GET',
        data: {
            app_id,
            publish_status,
        },
    });
};

// Get workflow scheduled task
// @param {string} app_id - Application ID of the workflow
// @param {string} workflow_id - Workflow ID
// @returns {Promise<any>} - Returns a Promise object with the scheduled task information
export const getWorkflowScheduledTask = async (app_id: string | number, workflow_id: string | number) => {
    return await aniRequest<any>(`/v1/scheduled_tasks/workflow/${app_id}/${workflow_id}`, {
        method: 'GET',
    });
};

// Create workflow scheduled task
// @param {object} data - Task creation data
// @returns {Promise<any>} - Returns a Promise object with the creation result
export const createWorkflowScheduledTask = async (data: any) => {
    return await aniRequest<any>(`/v1/scheduled_tasks/create`, {
        method: 'POST',
        data,
    });
};

// Update workflow scheduled task
// @param {string | number} task_id - Task ID
// @param {object} data - Task update data
// @returns {Promise<any>} - Returns a Promise object with the update result
export const updateWorkflowScheduledTask = async (task_id: string | number, data: any) => {
    return await aniRequest<any>(`/v1/scheduled_tasks/update/${task_id}`, {
        method: 'PUT',
        data,
    });
};

// Delete workflow scheduled task
// @param {string | number} task_id - Task ID
// @returns {Promise<any>} - Returns a Promise object with the deletion result
export const deleteWorkflowScheduledTask = async (task_id: string | number) => {
    return await aniRequest<any>(`/v1/scheduled_tasks/delete/${task_id}`, {
        method: 'DELETE',
    });
};

// Run workflow
// @param {string} app_id - Application ID of the workflow
// @param {object} params - Run parameters
// @returns {Promise<any>} - Returns a Promise object with the run result
export const runWorkFlow = async (app_id, params) => {
    return await aniRequest<any>(`/v1/workflow/run`, {
        method: 'POST',
        data: {
            app_id,
            run_type: 0,
            run_name: 1,
            ...params,
        },
    });
};

// Run node
// @param {string} app_id - Application ID of the node
// @param {object} params - Run parameters
// @returns {Promise<any>} - Returns a Promise object with the run result
export const runNode = async (app_id, params) => {
    return await aniRequest<any>(`/v1/workflow/node_run`, {
        method: 'POST',
        data: {
            app_id,
            ...params,
        },
    });
};

// Get processing information
// @param {string} exec_id - Execution ID
// @returns {Promise<any>} - Returns a Promise object with the processing information
export const getDealtWithInfo = async exec_id => {
    if (!exec_id) {
        return Promise.resolve({});
    }
    return await aniRequest<any>(`/v1/node/node_info/${exec_id}`, { method: 'GET' });
};

// Update processing information
// @param {string} exec_id - Execution ID
// @param {object} params - Update parameters
// @returns {Promise<any>} - Returns a Promise object with the update result
export const updateDealtWith = async (exec_id, params) => {
    return await aniRequest<any>(`/v1/node/node_update/${exec_id}`, {
        method: 'PUT',
        data: {
            ...params,
        },
    });
};

// Get workflow log list
// @param {object} params - Query parameters
// @returns {Promise<any>} - Returns a Promise object with the workflow log list
export const getWorkFlowLogList = async params => {
    return await aniRequest<any>(`/v1/workspace/workspace_workflow_log_list`, {
        method: 'POST',
        data: {
            page: params.current,
            page_size: params.pageSize,
            app_id: params.app_id,
            app_runs_name: params.app_runs_name,
            app_runs_status: params.app_runs_status,
        },
    });
};

// Publish workflow
// @param {string} app_id - Application ID of the workflow
// @returns {Promise<any>} - Returns a Promise object with the publish result
export const publishWorkFlow = async app_id => {
    return await aniRequest<any>(`/v1/workflow/publish/${app_id}`, { method: 'PUT' });
};

// Get recently active list
// @param {object} params - Query parameters
// @returns {Promise<any>} - Returns a Promise object with the recently active list
export const getRecentlyActiveList = async params => {
    return await aniRequest<any>(`/v1/workspace/workspace_list`, {
        method: 'POST',
        data: {
            page: params.current,
            page_size: params.pageSize,
        },
    });
};

// Get backlogs list
// @param {object} params - Query parameters
// @returns {Promise<any>} - Returns a Promise object with the backlogs list
export const getBacklogsList = async params => {
    return await aniRequest<any>(`/v1/node/backlog_list`, {
        method: 'GET',
        data: {
            page: params.current,
            page_size: params.pageSize,
        },
    });
};

// Get workflow process list
// @param {object} params - Query parameters
// @returns {Promise<any>} - Returns a Promise object with the workflow process list
export const getWorkFlowProcessList = async params => {
    return await aniRequest<any>(`/v1/workspace/workspace_workflow_process_log`, {
        method: 'POST',
        data: {
            page: params.current,
            page_size: params.pageSize,
            show_status: params.showStatus || 0,
        },
    });
};

// Get workflow log information
// @param {string} id - Log IDimage.png
// @returns {Promise<any>} - Returns a Promise object with the workflow log information
export const getWorkFlowLogInfo = async (id, run_id) => {
    return await aniRequest<any>(`/v1/workspace/workspace_workflow_log_info`, {
        method: 'POST',
        data: {
            workflows_id: id,
            app_runs_id: run_id,
        },
    });
};

// Get workflow start condition
// @param {string} app_id - Application ID of the workflow
// @returns {Promise<any>} - Returns a Promise object with the workflow start condition
export const getWorkFlowStartCondition = async app_id => {
    return await aniRequest<any>(`/v1/workflow/workflow_start_condition/${app_id}`, {
        method: 'GET',
    });
};

// Get tool authorization status
// @param {string} app_id - Application ID of the tool
// @returns {Promise<any>} - Returns a Promise object with the tool authorization status
export const getToolAuthorizationStatus = async (name, data) => {
    return await aniRequest<any>(`/v1/tool/tools_authorization/${name}`, { method: 'PUT', data });
};

export const delToolAuthorization = async (name) => {
    return await aniRequest<any>(`/v1/tool/tools_delete_authorization/${name}`, { method: 'DELETE' });
};

export const getToolDetail = async (name) => {
    return await aniRequest<any>(`/v1/tool/tool_detail/${name}`, { method: 'GET' });
};

/**
 * Get node confirm user list
 * @returns {Promise<any>} Returns a Promise object with the node confirm user list
 */
export const getNodeConfirmUserList = async () => {
    return await aniRequest<any>(`/v1/auth/team_member_list`, { method: 'GET' });
};

/**
 * Set language
 * @param {string} language - Language code
 * @returns {Promise<any>} Returns a Promise object with the result of setting the language
 */
export const setLang = async language => {
    return await aniRequest<any>(`/v1/auth/switch_the_language`, {
        method: 'POST',
        data: {
            language,
        },
    });
};

export const importWorkflow = async (data: any) => {
    return await aniRequest<any>(`/v1/workflow/import`, {
        method: 'POST',
        data: data,
    });
};

export const exportWorkflow = async (app_id: string, publish_status: number = 0) => {
    return await aniRequest<any>(`/v1/workflow/export/${app_id}`, {
        method: 'GET',
        data: {
            publish_status,
        },
    });
};

export const getTagList = async (mode: Number) => {
    return await aniRequest<any>(`/v1/tag/tags`, {
        method: 'GET',
        data: {
            mode,
        },
    });
};
export const createTag = async (name: string, mode = 0) => {
    return await aniRequest<any>(`/v1/tag/tags`, {
        method: 'POST',
        data: {
            name,
            mode,
        },
    });
};

export const deleteTag = async tag_id => {
    return await aniRequest<any>(`/v1/tag/tags/${tag_id}`, {
        method: 'DELETE',
    });
};

export const bindTag = async (tag_ids = [], app_ids = []) => {
    return await aniRequest<any>(`/v1/tag/tags_bindings`, {
        method: 'POST',
        data: {
            tag_ids,
            app_ids,
        },
    });
};

export const unBindTag = async (tag_ids = [], app_id) => {
    return await aniRequest<any>(`/v1/tag/tags_bindings`, {
        method: 'DELETE',
        data: {
            tag_ids,
            app_id,
        },
    });
};

export const updateTag = async (tag_id, name: string) => {
    return await aniRequest<any>(`/v1/tag/tags/${tag_id}`, {
        method: 'PUT',
        data: {
            name,
        },
    });
};

// Get workflow list
// @param {number} type - Workflow search type, default is 1
// @returns {Promise<any>} - Returns a Promise object with the workflow list
export const getWorkflowList = async (type = 1) => {
    return await aniRequest<any>(`/v1/workflow/workflows_list`, {
        method: 'GET',
        data: {
            page_size: 999999,
            workflows_search_type: type,
        },
    });
};

/**
 * Interface for tag data structure
 * @interface Tag
 * @property {number} id - The unique identifier of the tag
 * @property {string} name - The name of the tag
 */
interface Tag {
    id: number;
    name: string;
}

/**
 * Parameters for app list query
 * @interface AppListParams
 */
interface AppListParams {
    page?: number;
    page_size?: number;
    search_type?: number;
    apps_name?: string;
    apps_mode?: '1' | '2' | '3' | '4' | string;
    tag_ids?: string;
}

/**
 * App list item data structure
 * @interface AppListItem
 * @property {number} app_id - The unique identifier of the app
 * @property {string} name - App name
 * @property {number} mode - App mode
 * @property {string} description - App description
 * @property {string} icon - App icon URL
 * @property {string} icon_background - Icon background color
 * @property {number} execution_times - Number of executions
 * @property {number} publish_status - Publication status
 * @property {string} published_time - Last publication time
 * @property {string} published_creator - Publisher name
 * @property {Tag[]} [tags] - Associated tags
 * @property {Object[]} [list] - Sub-apps list
 * @property {number} list[].apps_id - Sub-app ID
 * @property {string} list[].name - Sub-app name
 * @property {number} list[].mode - Sub-app mode
 * @property {string} list[].icon - Sub-app icon URL
 * @property {string} list[].icon_background - Sub-app icon background
 */
interface AppListItem {
    app_id: number;
    name: string;
    mode: number;
    description: string;
    icon: string;
    icon_background: string;
    execution_times: number;
    publish_status: number;
    published_time: string;
    published_creator: string;
    tags?: Tag[];
    list?: Array<{
        apps_id: number;
        name: string;
        mode: number;
        icon: string;
        icon_background: string;
    }>;
}

/**
 * Response structure for app list API
 * @interface AppListResponse
 * @property {number} code - Response code (0 for success)
 * @property {string} detail - Response message
 * @property {Object} data - Response data
 * @property {AppListItem[]} data.list - List of apps
 * @property {number} data.total_count - Total number of items
 * @property {number} data.total_pages - Total number of pages
 * @property {number} data.page - Current page number
 * @property {number} data.page_size - Items per page
 */
interface AppListResponse {
    code: number;
    detail: string;
    data: {
        list: AppListItem[];
        total_count: number;
        total_pages: number;
        page: number;
        page_size: number;
    };
}

/**
 * Fetch app list with filters and pagination
 * @async
 * @param {Partial<AppListParams>} params - Query parameters
 * @returns {Promise<AppListResponse>} App list response
 * @example
 * // Get personal agent apps
 * const response = await getAppList({
 *   search_type: 1,
 *   apps_mode: '1'
 * });
 */
export const getAppList = async (params: Partial<AppListParams>) => {
    return await aniRequest<AppListResponse>(`/v1/apps/apps_list`, {
        method: 'GET',
        data: {
            page: 1,
            page_size: 999999,
            ...params,
        },
    });
};
type AppMode = 'agent' | 'workflow' | 'knowledge' | 'skill';

const APP_MODE_MAP: Record<AppMode, '1' | '2' | '3' | '4'> = {
    agent: '1',
    workflow: '2',
    knowledge: '3',
    skill: '4',
};

interface GetAppListOptions {
    search_type?: number;
    apps_name?: string;
    tag_ids?: string;
    page?: number;
    page_size?: number;
}

/**
 * Enhanced app list fetcher with type-safe mode selection
 * @param mode - The type(s) of apps to fetch, can be single mode or array of modes
 * @param options - Additional options for the request
 * @example
 * // Single mode
 * await getAppListByMode('agent')
 * // Multiple modes
 * await getAppListByMode(['agent', 'skill'])
 */
export const getAppListByMode = async (
    mode: AppMode | AppMode[],
    options: GetAppListOptions = {},
) => {
    const modes = Array.isArray(mode) ? mode : [mode];
    const appModes = modes.map(m => APP_MODE_MAP[m]).join(',') as AppListParams['apps_mode'];

    return await getAppList({
        ...options,
        apps_mode: appModes,
    });
};

/**
 * Generate an agent based on user prompt
 * @async
 * @param {string} user_prompt - The prompt text to generate agent
 * @returns {Promise<ApiResponse>} Generated agent data
 */
export const agentGenerate = async (user_prompt: string) => {
    return await aniRequest<any>(`/v1/agent/agent_generate`, {
        method: 'POST',
        data: { user_prompt },
    });
};

/**
 * Regenerate an agent with existing run ID
 * @async
 * @param {string} app_run_id - The run ID of the agent to regenerate
 * @returns {Promise<ApiResponse>} Regenerated agent data
 */
export const agentReGenerate = async (app_run_id: string) => {
    return await aniRequest<any>(`/v1/agent/agent_regenerate`, {
        method: 'POST',
        data: { app_run_id },
    });
};

/**
 * Supplement an existing agent with additional prompt
 * @async
 * @param {string} supplement_prompt - Additional prompt text
 * @param {string} app_run_id - The run ID of the agent to supplement
 * @returns {Promise<ApiResponse>} Updated agent data
 */
export const agentSupplement = async (supplement_prompt: string, app_run_id: string) => {
    return await aniRequest<any>(`/v1/agent/agent_supplement`, {
        method: 'POST',
        data: { supplement_prompt, app_run_id },
    });
};

interface AgentAbility {
    content: string;
    name: string;
    output_format: number;
    status: number;
}

interface AgentData {
    abilities: AgentAbility[];
    description: string;
    name: string;
    obligations: string;
    tags: number[];
}

interface AgentBatchCreateParams {
    agents: AgentData[];
}

export const agentCreate = async (data: AgentBatchCreateParams) => {
    return await aniRequest<any>(`/v1/agent/agent_create`, {
        method: 'POST',
        data: data,
    });
};

interface BatchAgentCreateParams {
    app_run_id: number;
    loop_count: number;
    loop_limit: number;
    supplement_prompt: string;
    loop_id: number;
}

export const batchAgentCreate = async (params: BatchAgentCreateParams) => {
    return await aniRequest<any>(`/v1/agent/agent_batch_generate`, {
        method: 'POST',
        data: params,
    });
};

export const previewBatchAgent = async (supplement_prompt: string, app_run_id: string) => {
    return await aniRequest<any>(`/v1/agent/agent_batch_sample`, {
        method: 'POST',
        data: { supplement_prompt, app_run_id },
    });
};

interface AgentInfo {
    name: string;
    type: string;
    value: {
        abilities: Array<{
            content: string;
            name: string;
            output_format: number;
        }>;
        description: string;
        name: string;
        obligations: string;
    };
}

interface SaveAgentParams {
    app_run_id: number;
    record_id: number;
    agent_info: AgentInfo;
}

export const saveAgentTemporarily = async (params: SaveAgentParams) => {
    return await aniRequest<any>(`/v1/agent/agent_save`, {
        method: 'POST',
        data: params,
    });
};














export const skillCreate = async (user_prompt:string ) => {
    return await aniRequest<any>(`/v1/skill/skill_generate`, {
        method: 'POST',
        data: {
            user_prompt
        },
    });
};



export const skillRun = async (skill_id:string,input_dict) => {
    return await aniRequest<any>(`/v1/skill/skill_run`, {
        method: 'POST',
        data: {
            skill_id,input_dict
        },
    });
};

export const skillDebug = async (debugData:any) => {
    return await aniRequest<any>(`/v1/skill/skill_debug`, {
        method: 'POST',
        data:debugData,
    });
};
export const skillCorrection = async (app_run_id:string,correction_prompt) => {
    return await aniRequest<any>(`/v1/skill/skill_correction`, {
        method: 'POST',
        data: {
            app_run_id,correction_prompt
        },
    });
};
export const skillDataCreate= async (createData) => {
    return await aniRequest<any>(`/v1/skill/skill_data_create`, {
        method: 'POST',
        data:createData,
    });
};

// Pause or resume workflow run
// @param {number} app_run_id - App run ID
// @param {number} paused - Pause status (0: resume, 1: pause)
// @returns {Promise<any>} - Returns a Promise object with the pause/resume result
export const pauseResumeWorkflow = async (app_run_id: number, paused: number) => {
    return await aniRequest<any>(`/v1/workflow/paused`, {
        method: 'POST',
        data: {
            app_run_id,
            paused,
        },
    });
};