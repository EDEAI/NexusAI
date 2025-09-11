/*
 * @LastEditors: biz
 */

import { checkViewInIframe, getIframeApiUrl } from '@/utils/fullscreenStorage';
import aniRequest from './request';

const agent_info = '/v1/agent/agent_info/';
const dataset_list = '/v1/vector/dataset_list/2';
const agent_base_update = '/v1/agent/agent_base_update/';
const agent_abilities_set = '/v1/agent/agent_abilities_set/';
const agent_output_set = '/v1/agent/agent_output_set/';
const agent_engine_set = '/v1/agent/agent_engine_set/';
const agent_publish = '/v1/agent/agent_publish/';
const agent_run = '/v1/agent/agent_run';

export const GetagentInfo = async (app_id: any, publish_status?: any) => {
    const data={
        publish_status: publish_status == 'true' ? 1 : 0,
    }
    if(checkViewInIframe()){
        data.chat_base_url = getIframeApiUrl(true);
    }
    const res = await aniRequest<any>(`${agent_info}${app_id}`, {
        method: 'GET',
        data,
    });
    return res;
};

export const GetdatasetList = async () => {
    const res = await aniRequest<any>(`${dataset_list}`, { method: 'GET' });
    return res;
};

export const PutagentBaseupdate = async (data: any) => {
    const res = await aniRequest<any>(`${agent_base_update}${data.agent_id}`, {
        method: 'PUT',
        data: data.data,
    });
    return res;
};

export const PutagentAbilitiesset = async (data: any) => {
    const res = await aniRequest<any>(`${agent_abilities_set}${data.agent_id}`, {
        method: 'PUT',
        data: data.data,
    });
    return res;
};
export const PutagentOutputset = async (data: any) => {
    const res = await aniRequest<any>(`${agent_output_set}${data.agent_id}`, {
        method: 'PUT',
        data: data,
    });
    return res;
};
export const PutagentEngineset = async (data: any) => {
    const res = await aniRequest<any>(`${agent_engine_set}${data.agent_id}`, {
        method: 'PUT',
        data: data.data,
    });
    return res;
};
export const PutagentPublish = async (agent_id: any) => {
    const res = await aniRequest<any>(`${agent_publish}${agent_id}`, { method: 'PUT' });
    return res;
};
export const PutagentRun = async (data: any) => {
    const res = await aniRequest<any>(`${agent_run}`, { method: 'POST', data: data });
    return res;
};

export const postAgentChatMessage = async (data: any) => {
    const res = await aniRequest<any>(`/v1/agent/agent_chat_message`, {
        method: 'POST',
        data: data,
    });
    return res;
};

export const getAgentMessageHistory = async (agent_id: string,page:number) => {
    const res = await aniRequest<any>(`/v1/agent/${agent_id}/agent_message_list`, {
        method: 'GET',
        data:{
            page,
            page_size:20
        }
    });
    return res;
};

export const getAgentLogList = async (app_id: string,data:any) => {
    const res = await aniRequest<any>(`/v1/agent/${app_id}/agent_log_list`, {
        method: 'GET',
        data
    });
    return res;
};
export const getAgentLogDetail = async (app_id: string, app_run_id: string) => {
    const res = await aniRequest<any>(`/v1/agent/${app_id}/agent_log_details`, {
        method: 'GET',
        data: {
            app_run_id,
        },
    });
    return res;
};
export const clearAgentMessageMemory = async (agent_id: string, message_id: number) => {
    const res = await aniRequest<any>(`/v1/agent/${agent_id}/clear_agent_chat_memory`, {
        method: 'POST',
        data: {
            message_id,
            agent_id,
        },
    });
    return res;
};
