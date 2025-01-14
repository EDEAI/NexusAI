import { data } from 'autoprefixer';
import aniRequest from './request';

// Get homepage
export const getIndex = async () => {
    const res = await aniRequest<any>('/v1/index/', { method: 'GET' });
    return res;
};

// Get list
export const getList = async (URL: string, data: any) => {
    const res = await aniRequest<any>(URL, { method: 'GET', data: data });
    return res;
};

// Get chatroom list
export const getChatroom = async (data: any) => {
    const res = await aniRequest<any>('/v1/chatroom/', { method: 'GET', data: data });
    return res;
};

// Delete chatroom
export const delChatroom = async (data: any) => {
    const res = await aniRequest<any>(`/v1/chatroom/${data.id}`, { method: 'DELETE' });
    return res;
};

// Create chatroom
export const createRoom = async (data: any) => {
    const res = await aniRequest<any>('/v1/chatroom/', { method: 'POST', data: data });
    return res;
};

// Chatroom details
export const roomDetails = async (data: any) => {
    const res = await aniRequest<any>(`/v1/chatroom/${data.id}/details`, { method: 'GET' });
    return res;
};

// Recently viewed chatrooms
export const roomRecent = async (data: any) => {
    const res = await aniRequest<any>(`/v1/chatroom/recent`, {
        method: 'GET',
        data: { chatroom_id: data.id },
    });
    return res;
};

// Update chatroom
export const updataRoom = async (data: any, id: any) => {
    const res = await aniRequest<any>(`/v1/chatroom/${id}/update_chatroom`, {
        method: 'POST',
        data: data,
    });
    return res;
};

// Chatroom auto-reply switch
export const upRoomStatus = async (data: any, id: any) => {
    const res = await aniRequest<any>(`/v1/chatroom/${id}/smart_selection`, {
        method: 'POST',
        data: data,
    });
    return res;
};

// Agent auto-reply switch
export const upAgentStatus = async (data: any, id: any, agentId: any) => {
    const res = await aniRequest<any>(`/v1/chatroom/${id}/agents/${agentId}/setting`, {
        method: 'PUT',
        data: data,
    });
    return res;
};

// Get chatroom messages
export const getRoomMessage = async (id: any, data: any) => {
    const res = await aniRequest<any>(`/v1/chatroom/${id}/chatroom_message`, {
        method: 'GET',
        data: data,
    });
    return res;
};

// meeting summary

export const getMeetingsummary = async (id: any,data:any) => {
    const res = await aniRequest<any>(`/v1/chatroom/${id}/chat_history_message_summary`, {
        method: 'POST',
        data: data,
    });
    return res;
};

export const getMeetingOrientation = async (id: any,data:any) => {
    const res = await aniRequest<any>(`/v1/chatroom/${id}/chat_history_summary`, {
        method: 'POST',
        data: data,
    });
    return res;
};

export const getMeetingSummaryHistory = async(data:any)=>{
    const res = await aniRequest<any>(`/v1/chatroom/chat_room_history`, {
        method: 'GET',
        data: data,
    });
    return res;
    
} 