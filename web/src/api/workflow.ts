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
            page_size: 100,
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
            page_size: 100,
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
        },
    });
};

// Get workflow log information
// @param {string} id - Log ID
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
