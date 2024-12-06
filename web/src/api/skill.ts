import aniRequest from './request';

const skill_info = '/v1/skill/skill_info/'; // Get skill card detail information {app_id} Status publish_status 0/1
const skill_update = '/v1/skill/skill_update/'; // Update skill card information {app_id}
const skill_publish = '/v1/skill/skill_publish/'; // Publish skill card information {app_id}
const skill_run = '/v1/skill/skill_run'; // Delete skill card information

export const GetskillInfo = async (app_id: any, publish_status?: any) => {
    const res = await aniRequest<any>(`${skill_info}${app_id}`, {
        method: 'GET',
        data: { publish_status: publish_status == 'true' ? 1 : 0 },
    });
    return res;
};

export const PutskillUpdate = async (data: any) => {
    const res = await aniRequest<any>(`${skill_update}${data.app_id}`, {
        method: 'PUT',
        data: data.data,
    });
    return res;
};

export const PutskillPublish = async (app_id: any) => {
    const res = await aniRequest<any>(`${skill_publish}${app_id}`, { method: 'PUT' });
    return res;
};

export const PostskillRun = async (data: any) => {
    const res = await aniRequest<any>(`${skill_run}`, { method: 'POST', data: data });
    return res;
};