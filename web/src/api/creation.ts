/*
 * @LastEditors: biz
 */
import aniRequest from './request';

const apps_list = '/v1/apps/apps_list'; // Get list information

//  1: agent 2: workflow 3: dataset 4: skill
const agent_delete = '/v1/agent/agent_delete/'; // Agent delete {appid} ok
const workflow_delete = '/v1/workflow/workflow_app_delete/'; // Workflow delete {app_id} ok
const dataset_delete = '/v1/vector/delete_dataset/'; // DATASET delete {app_id}
const skill_delete = '/v1/skill/delete_skill_by_app_id/'; // Skill delete {app_id}

const apps_create = '/v1/apps/apps_create'; // Create application
const apps_update = '/v1/apps/app_update/'; // Update application {appid}

export const GetChatroom = async (data: any) => {
    const res = await aniRequest<any>(`${apps_list}`, { method: 'GET', data: data });
    return res;
};

// export const DeleteCreation = async (data: any) => {
//     console.log(data)
//     const res = await aniRequest<any>(`${data.mode == 1 ? agent_delete :
//             data.mode == 2 ? workflow_delete :
//                 data.mode == 3 ? dataset_delete : skill_delete}
//                     ${data.app_id}/${data.mode == 4 ? '1' : ''}`, { method: 'DELETE', data: { app_id: data.app_id } });
//     return res;
// }

export const DeleteCreation = async (data: any) => {
    console.log(data);
    const res =
        (await data.mode) == 1
            ? aniRequest<any>(`${agent_delete}${data.app_id}`, { method: 'DELETE' })
            : data.mode == 2
            ? aniRequest<any>(`${workflow_delete}${data.app_id}`, { method: 'DELETE' })
            : data.mode == 3
            ? aniRequest<any>(`${dataset_delete}${data.app_id}`, { method: 'DELETE' })
            : aniRequest<any>(`${skill_delete}${data.app_id}`, {
                  method: 'DELETE',
                  data: { is_soft: 1 },
              });
    return res;
};

export const PostappsCreate = async (data: any) => {
    const res = await aniRequest<any>(`${apps_create}`, { method: 'POST', data: data });
    return res;
};

export const PutappsUpdate = async (data: any) => {
    const res = await aniRequest<any>(`${apps_update}${data.app_id}`, {
        method: 'PUT',
        data: data,
    });
    return res;
};