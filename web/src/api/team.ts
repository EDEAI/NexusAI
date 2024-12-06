import aniRequest from './request';

// Get team list
export const getTeamList = async () => {
    return await aniRequest<any>(`/v1/auth/team_member_list`, { method: 'GET' });
};

// Generate invitation link
export const postInviteUser = async (data: any) => {
    return await aniRequest<any>(`/v1/auth/invite_user`, { method: 'POST', data: data });
};

// Register invited user account
export const postRegisterUser = async (data: any) => {
    return await aniRequest<any>(`/v1/auth/register_user`, { method: 'POST', data: data });
};